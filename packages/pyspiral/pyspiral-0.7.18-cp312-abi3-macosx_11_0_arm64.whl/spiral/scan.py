from functools import partial
from typing import TYPE_CHECKING, Any, Optional

import pyarrow as pa

from spiral.core.client import Shard, ShuffleConfig
from spiral.core.table import KeyRange
from spiral.core.table import Scan as CoreScan
from spiral.core.table.spec import Schema
from spiral.settings import CI, DEV

if TYPE_CHECKING:
    import dask.dataframe as dd
    import datasets.iterable_dataset as hf  # noqa
    import pandas as pd
    import polars as pl
    import streaming  # noqa
    import torch.utils.data as torchdata  # noqa

    from spiral.client import Spiral
    from spiral.dataloader import SpiralDataLoader, World  # noqa


class Scan:
    """Scan object."""

    def __init__(self, spiral: "Spiral", core: CoreScan):
        self.spiral = spiral
        self.core = core

    @property
    def metrics(self) -> dict[str, Any]:
        """Returns metrics about the scan."""
        return self.core.metrics()

    @property
    def schema(self) -> Schema:
        """Returns the schema of the scan."""
        return self.core.schema()

    @property
    def key_schema(self) -> Schema:
        """Returns the key schema of the scan."""
        return self.core.key_schema()

    def is_empty(self) -> bool:
        """Check if the Spiral is empty for the given key range.

        False negatives are possible, but false positives are not,
            i.e. is_empty can return False and scan can return zero rows.
        """
        return self.core.is_empty()

    def to_record_batches(
        self,
        *,
        key_range: KeyRange | None = None,
        key_table: pa.Table | pa.RecordBatchReader | None = None,
        batch_size: int | None = None,
        batch_readahead: int | None = None,
        hide_progress_bar: bool = False,
    ) -> pa.RecordBatchReader:
        """Read as a stream of RecordBatches.

        Args:
            key_range: Optional key range to filter the scan.
                If provided, the scan will only return rows within the key range.
                Only one of key_range or key_table can be provided.
            key_table: a table of keys to "take" (including aux columns for cell-push-down).
                If None, the scan will be executed without a key table.
            batch_size: the maximum number of rows per returned batch.
                This is currently only respected when the key_table is used. If key table is a
                RecordBatchReader, the batch_size argument must be None, and the existing batching is respected.
            batch_readahead: the number of batches to prefetch in the background.
            hide_progress_bar: If True, disables the progress bar during reading.
        """
        if key_range is not None and key_table is not None:
            raise ValueError("Only one of key_range or key_table can be provided.")

        if isinstance(key_table, pa.RecordBatchReader):
            if batch_size is not None:
                raise ValueError(
                    "batch_size must be None when key_table is a RecordBatchReader, the existing batching is respected."
                )
        elif isinstance(key_table, pa.Table):
            key_table = key_table.to_reader(max_chunksize=batch_size)

        return self.core.to_record_batches(
            key_range=key_range, key_table=key_table, batch_readahead=batch_readahead, progress=(not hide_progress_bar)
        )

    def to_unordered_record_batches(
        self,
        *,
        key_table: pa.Table | pa.RecordBatchReader | None = None,
        batch_size: int | None = None,
        batch_readahead: int | None = None,
        hide_progress_bar: bool = False,
    ) -> pa.RecordBatchReader:
        """Read as a stream of RecordBatches, NOT ordered by key.

        Args:
            key_table: a table of keys to "take" (including aux columns for cell-push-down).
                If None, the scan will be executed without a key table.
            batch_size: the maximum number of rows per returned batch.
                This is currently only respected when the key_table is used. If key table is a
                RecordBatchReader, the batch_size argument must be None, and the existing batching is respected.
            batch_readahead: the number of batches to prefetch in the background.
            hide_progress_bar: If True, disables the progress bar during reading.
        """
        if isinstance(key_table, pa.RecordBatchReader):
            if batch_size is not None:
                raise ValueError(
                    "batch_size must be None when key_table is a RecordBatchReader, the existing batching is respected."
                )
        elif isinstance(key_table, pa.Table):
            key_table = key_table.to_reader(max_chunksize=batch_size)

        return self.core.to_unordered_record_batches(
            key_table=key_table, batch_readahead=batch_readahead, progress=(not hide_progress_bar)
        )

    def to_table(
        self,
        *,
        key_range: KeyRange | None = None,
        key_table: pa.Table | pa.RecordBatchReader | None = None,
    ) -> pa.Table:
        """Read into a single PyArrow Table.

        Args:
            key_range: Optional key range to filter the scan.
                If provided, the scan will only return rows within the key range.
                Only one of key_range or key_table can be provided.
            key_table: a table of keys to "take" (including aux columns for cell-push-down).
                If None, the scan will be executed without a key table.
        """
        # NOTE: Evaluates fully on Rust side which improved debuggability.
        if DEV and not CI and key_table is None and key_range is None:
            rb = self.core.to_record_batch()
            return pa.Table.from_batches([rb])

        return self.to_record_batches(key_range=key_range, key_table=key_table).read_all()

    def to_dask(self) -> "dd.DataFrame":
        """Read into a Dask DataFrame.

        Requires the `dask` package to be installed.

        Dask execution has some limitations, e.g. UDFs are not currently supported. These limitations
        usually manifest as serialization errors when Dask workers attempt to serialize the state. If you are
        encountering such issues, please reach out to the support for assistance.
        """
        import dask.dataframe as dd

        _read_shard = partial(
            _read_shard_task,
            settings_json=self.spiral.config.to_json(),
            state_json=self.core.plan_state().to_json(),
        )
        return dd.from_map(_read_shard, self.shards())

    def to_pandas(self, *, key_range: KeyRange | None = None) -> "pd.DataFrame":
        """Read into a Pandas DataFrame.

        Requires the `pandas` package to be installed.
        """
        return self.to_table(key_range=key_range).to_pandas()

    def to_polars(self) -> "pl.DataFrame":
        """Read into a Polars DataFrame.

        Requires the `polars` package to be installed.
        """
        import polars as pl

        return pl.from_arrow(self.to_record_batches())

    def to_data_loader(
        self, seed: int = 42, shuffle_buffer_size: int = 8192, batch_size: int = 32, **kwargs
    ) -> "SpiralDataLoader":
        """Read into a Torch-compatible DataLoader for single-node training.

        Args:
            seed: Random seed for reproducibility.
            shuffle_buffer_size: Size of shuffle buffer.
            batch_size: Batch size.
            **kwargs: Additional arguments passed to SpiralDataLoader constructor.

        Returns:
            SpiralDataLoader with shuffled shards.
        """
        from spiral.dataloader import SpiralDataLoader

        return SpiralDataLoader(
            self, seed=seed, shuffle_buffer_size=shuffle_buffer_size, batch_size=batch_size, **kwargs
        )

    def to_distributed_data_loader(
        self,
        world: Optional["World"] = None,
        shards: list[Shard] | None = None,
        seed: int = 42,
        shuffle_buffer_size: int = 8192,
        batch_size: int = 32,
        **kwargs,
    ) -> "SpiralDataLoader":
        """Read into a Torch-compatible DataLoader for distributed training.

        Args:
            world: World configuration with rank and world_size.
                If None, auto-detects from torch.distributed.
            shards: Optional sharding. Sharding is global, i.e. the world will be used to select
                the shards for this rank. If None, uses scan's natural sharding.
            seed: Random seed for reproducibility.
            shuffle_buffer_size: Size of shuffle buffer.
                Use zero to skip shuffling with shuffle buffer.
            batch_size: Batch size.
            **kwargs: Additional arguments passed to SpiralDataLoader constructor.

        Returns:
            SpiralDataLoader with shards partitioned for this rank.

        Auto-detect from PyTorch distributed:
        ```python
        loader: SpiralDataLoader = scan.to_distributed_data_loader(batch_size=32)
        ```

        Explicit world configuration:
        ```python
        world = World(rank=0, world_size=4)
        loader: SpiralDataLoader = scan.to_distributed_data_loader(world=world, batch_size=32)
        ```
        """
        from spiral.dataloader import SpiralDataLoader, World

        if world is None:
            world = World.from_torch()

        shards = shards or self.shards()
        # Apply world partitioning to shards.
        shards = world.shards(shards, seed)

        return SpiralDataLoader(
            self,
            shards=shards,
            shuffle_shards=False,  # Shards are shuffled before selected for the world.
            seed=seed,
            shuffle_buffer_size=shuffle_buffer_size,
            batch_size=batch_size,
            **kwargs,
        )

    def resume_data_loader(self, state: dict[str, Any], **kwargs) -> "SpiralDataLoader":
        """Create a DataLoader from checkpoint state, resuming from where it left off.

        This is the recommended way to resume training from a checkpoint. It extracts
        the seed, samples_yielded, and shards from the state dict and creates a new
        DataLoader that will skip the already-processed samples.

        Args:
            state: Checkpoint state from state_dict().
            **kwargs: Additional arguments to pass to SpiralDataLoader constructor.
                These will override values in the state dict where applicable.

        Returns:
            New SpiralDataLoader instance configured to resume from the checkpoint.

        Save checkpoint during training:
        ```python
        loader = scan.to_distributed_data_loader(batch_size=32, seed=42)
        checkpoint = loader.state_dict()
        ```

        Resume later - uses same shards from checkpoint:
        ```python
        resumed_loader = scan.resume_data_loader(
            checkpoint,
            batch_size=32,
            transform_fn=my_transform,
        )
        """
        from spiral.dataloader import SpiralDataLoader

        return SpiralDataLoader.from_state_dict(self, state, **kwargs)

    def to_iterable_dataset(
        self,
        shards: list[Shard] | None = None,
        shuffle: ShuffleConfig | None = None,
        batch_readahead: int | None = None,
        infinite: bool = False,
    ) -> "hf.IterableDataset":
        """Returns a Huggingface's IterableDataset.

        Requires `datasets` package to be installed.

        Note: For new code, consider using SpiralDataLoader instead.

        Args:
            shards: Optional list of shards to read. If None, uses scan's natural sharding.
            shuffle: Optional ShuffleConfig for configuring within-shard sample shuffling.
                If None, no shuffling is performed.
            batch_readahead: Controls how many batches to read ahead concurrently.
                If pipeline includes work after reading (e.g. decoding, transforming, ...) this can be set higher.
                Otherwise, it should be kept low to reduce next batch latency. Defaults to 2.
            infinite: If True, the returned IterableDataset will loop infinitely over the data,
                re-shuffling ranges after exhausting all data.
        """
        stream = self.core.to_shuffled_record_batches(
            shards=shards,
            shuffle=shuffle,
            batch_readahead=batch_readahead,
            infinite=infinite,
        )

        from spiral.iterable_dataset import to_iterable_dataset

        return to_iterable_dataset(stream)

    def shards(self) -> list[Shard]:
        """Get list of shards for this scan.

        The shards are based on the scan's physical data layout (file fragments).
        Each shard contains a key range and cardinality (set to None when unknown).

        Returns:
            List of Shard objects with key range and cardinality (if known).

        """
        return self.core.shards()

    def _debug(self):
        # Visualizes the scan, mainly for debugging purposes.
        from spiral.debug.scan import show_scan

        show_scan(self.core)

    def _dump_manifests(self):
        # Print manifests in a human-readable format.
        from spiral.debug.manifests import display_scan_manifests

        display_scan_manifests(self.core)

    def _dump_metrics(self):
        # Print metrics in a human-readable format.
        from spiral.debug.metrics import display_metrics

        display_metrics(self.metrics)


# NOTE(marko): This function must be picklable!
def _read_shard_task(shard: Shard, *, settings_json: str, state_json: str) -> "pd.DataFrame":
    from spiral import Spiral
    from spiral.core.table import ScanState
    from spiral.settings import ClientSettings

    settings = ClientSettings.from_json(settings_json)
    sp = Spiral(config=settings)
    state = ScanState.from_json(state_json)
    task_scan = Scan(sp, sp.core.load_scan(state))

    return task_scan.to_record_batches(key_range=shard.key_range, hide_progress_bar=True).read_all().to_pandas()
