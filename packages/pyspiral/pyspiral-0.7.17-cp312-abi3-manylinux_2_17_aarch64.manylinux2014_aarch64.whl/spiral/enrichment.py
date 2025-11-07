from __future__ import annotations

import dataclasses
import logging
from functools import partial
from typing import TYPE_CHECKING

from spiral.core.client import KeyColumns, Shard
from spiral.core.table import KeyRange
from spiral.core.table.spec import Key, Operation
from spiral.expressions import Expr

if TYPE_CHECKING:
    import dask.distributed

    from spiral import Scan, Table

logger = logging.getLogger(__name__)


class Enrichment:
    """
    An enrichment is used to derive new columns from the existing once, such as fetching data from object storage
    with `se.s3.get` or compute embeddings. With column groups design supporting 100s of thousands of columns,
    horizontally expanding tables are a powerful primitive.

    NOTE: Spiral aims to optimize enrichments where source and destination table are the same.
    """

    def __init__(
        self,
        table: Table,
        projection: Expr,
        where: Expr | None,
    ):
        self._table = table
        self._projection = projection
        self._where = where

    @property
    def table(self) -> Table:
        """The table to write back into."""
        return self._table

    @property
    def projection(self) -> Expr:
        """The projection expression."""
        return self._projection

    @property
    def where(self) -> Expr | None:
        """The filter expression."""
        return self._where

    def _scan(self) -> Scan:
        return self._table.spiral.scan(self._projection, where=self._where, _key_columns=KeyColumns.Included)

    def apply(
        self,
        *,
        batch_readahead: int | None = None,
        partition_size_bytes: int | None = None,
        txn_dump: str | None = None,
    ) -> None:
        """Apply the enrichment onto the table in a streaming fashion.

        For large tables, consider using `apply_dask` for distributed execution.

        Args:
            index: Optional key space index to use for sharding the enrichment.
                If not provided, the table's default sharding will be used.
            partition_size_bytes: The maximum partition size in bytes.
                If not provided, the default partition size is used.
            txn_dump: Optional path to dump the transaction JSON for debugging.
        """

        txn = self._table.txn()

        txn.writeback(
            self._scan(),
            partition_size_bytes=partition_size_bytes,
            batch_readahead=batch_readahead,
        )

        if txn.is_empty():
            logger.warning("Transaction not committed. No rows were read for enrichment.")
            return

        txn.commit(txn_dump=txn_dump)

    def apply_dask(
        self,
        *,
        partition_size_bytes: int | None = None,
        shards: list[Shard] | None = None,
        txn_dump: str | None = None,
        checkpoint_dump: str | None = None,
        client: dask.distributed.Client | None = None,
        **kwargs,
    ) -> None:
        """Use distributed Dask to apply the enrichment. Requires `dask[distributed]` to be installed.

        If "address" of an existing Dask cluster is not provided in `kwargs`, a local cluster will be created.

        Dask execution has some limitations, e.g. UDFs are not currently supported. These limitations
        usually manifest as serialization errors when Dask workers attempt to serialize the state. If you are
        encountering such issues, consider splitting the enrichment into UDF-only derivation that will be
        executed in a streaming fashion, followed by a Dask enrichment for the rest of the computation.
        If that is not possible, please reach out to the support for assistance.

        Args:
            partition_size_bytes: The maximum partition size in bytes.
                If not provided, the default partition size is used.
            shards: Optional list of shards to use for the enrichment.
                If provided and checkpoint is present, the checkpoint shards will be used instead.
                If not provided, the table's default sharding will be used.
            txn_dump: Optional path to dump the transaction JSON for debugging.
            checkpoint_dump: Optional path to dump intermediate checkpoints for incremental progress.
            client: Optional Dask distributed client. If not provided, a new client will be created
            **kwargs: Additional keyword arguments to pass to `dask.distributed.Client`
                such as `address` to connect to an existing cluster.
        """
        if client is None:
            try:
                from dask.distributed import Client
            except ImportError:
                raise ImportError("dask is not installed, please install dask[distributed] to use this feature.")

            # Connect before doing any work.
            client = Client(**kwargs)

        # Start a transaction BEFORE the planning scan.
        tx = self._table.txn()
        plan_scan = self._scan()

        # Determine the "tasks".
        task_shards = None
        # Use checkpoint, if provided.
        if checkpoint_dump is not None:
            checkpoint: list[KeyRange] | None = _checkpoint_load_key_ranges(checkpoint_dump)
            if checkpoint is None:
                logger.info(f"No existing checkpoint found at {checkpoint_dump}. Starting from scratch.")
            else:
                logger.info(f"Resuming enrichment from checkpoint at {checkpoint_dump} with {len(checkpoint)} ranges.")
                task_shards = [Shard(kr, None) for kr in checkpoint]
        # Fallback to provided shards.
        if task_shards is None and shards is not None:
            task_shards = shards
        # Fallback to default sharding.
        if task_shards is None:
            task_shards = plan_scan.shards()

        # Partially bind the enrichment function.
        _compute = partial(
            _enrichment_task,
            settings_json=self._table.spiral.config.to_json(),
            state_json=plan_scan.core.plan_state().to_json(),
            output_table_id=self._table.table_id,
            partition_size_bytes=partition_size_bytes,
            incremental=checkpoint_dump is not None,
        )
        enrichments = client.map(_compute, task_shards)

        logger.info(f"Applying enrichment with {len(task_shards)} shards. Follow progress at {client.dashboard_link}")

        failed_ranges = []
        try:
            for result, shard in zip(client.gather(enrichments), task_shards):
                result: EnrichmentTaskResult

                if result.error is not None:
                    logger.error(f"Enrichment task failed for range {shard.key_range}: {result.error}")
                    failed_ranges.append(shard.key_range)
                    continue

                tx.include(result.ops)
        except Exception as e:
            # If not incremental, re-raise the exception.
            if checkpoint_dump is None:
                raise e

            # Handle worker failures (e.g., KilledWorker from Dask)
            from dask.distributed import KilledWorker

            if isinstance(e, KilledWorker):
                logger.error(f"Dask worker was killed during enrichment: {e}")

            # Try to gather partial results and mark remaining tasks as failed
            for future, shard in zip(enrichments, task_shards):
                if future.done() and not future.exception():
                    try:
                        result = future.result()

                        if result.error is not None:
                            logger.error(f"Enrichment task failed for range {shard.key_range}: {result.error}")
                            failed_ranges.append(shard.key_range)
                            continue

                        tx.include(result.ops)
                    except Exception:
                        # Task failed or incomplete, add to failed ranges
                        failed_ranges.append(shard.key_range)
                else:
                    # Task didn't complete, add to failed ranges
                    failed_ranges.append(shard.key_range)

        # Dump checkpoint of failed ranges, if any.
        if checkpoint_dump is not None:
            logger.info(
                f"Dumping checkpoint with failed {len(failed_ranges)}/{len(task_shards)} ranges to {checkpoint_dump}."
            )
            _checkpoint_dump_key_ranges(checkpoint_dump, failed_ranges)

        if tx.is_empty():
            logger.warning("Transaction not committed. No rows were read for enrichment.")
            return

        # Always compact in distributed enrichment.
        tx.commit(compact=True, txn_dump=txn_dump)


def _checkpoint_load_key_ranges(checkpoint_dump: str) -> list[KeyRange] | None:
    import json
    import os

    if not os.path.exists(checkpoint_dump):
        return None

    with open(checkpoint_dump) as f:
        data = json.load(f)
        return [
            KeyRange(begin=Key(bytes.fromhex(r["begin"])), end=Key(bytes.fromhex(r["end"])))
            for r in data.get("key_ranges", [])
        ]


def _checkpoint_dump_key_ranges(checkpoint_dump: str, ranges: list[KeyRange]):
    import json
    import os

    os.makedirs(os.path.dirname(checkpoint_dump), exist_ok=True)
    with open(checkpoint_dump, "w") as f:
        json.dump(
            {"key_ranges": [{"begin": bytes(r.begin).hex(), "end": bytes(r.end).hex()} for r in ranges]},
            f,
        )


@dataclasses.dataclass
class EnrichmentTaskResult:
    ops: list[Operation]
    error: str | None = None

    def __getstate__(self):
        return {
            "ops": [op.to_json() for op in self.ops],
            "error": self.error,
        }

    def __setstate__(self, state):
        self.ops = [Operation.from_json(op_json) for op_json in state["ops"]]
        self.error = state["error"]


# NOTE(marko): This function must be picklable!
def _enrichment_task(
    shard: Shard,
    *,
    settings_json: str,
    state_json: str,
    output_table_id,
    partition_size_bytes: int | None,
    incremental: bool,
) -> EnrichmentTaskResult:
    # Returns operations that can be included in a transaction.
    from spiral import Scan, Spiral
    from spiral.core.table import ScanState
    from spiral.settings import ClientSettings

    settings = ClientSettings.from_json(settings_json)
    sp = Spiral(config=settings)
    state = ScanState.from_json(state_json)
    task_scan = Scan(sp, sp.core.load_scan(state))
    table = sp.table(output_table_id)
    task_tx = table.txn()

    try:
        task_tx.writeback(task_scan, key_range=shard.key_range, partition_size_bytes=partition_size_bytes)
        return EnrichmentTaskResult(ops=task_tx.take())
    except Exception as e:
        task_tx.abort()

        if incremental:
            return EnrichmentTaskResult(ops=[], error=str(e))

        logger.error(f"Enrichment task failed for shard {shard}: {e}")
        raise e
