# Copyright (c) 2022, California Institute of Technology and contributors
#
# You should have received a copy of the licensing terms for this
# software included in the file "LICENSE" located in the top-level
# directory of this package. If you did not, you can view a copy at
# https://git.ligo.org/ngdd/arrakis-server/-/raw/main/LICENSE

from __future__ import annotations

import argparse
import logging
import random
import string
import sys
import threading
from collections import defaultdict
from collections.abc import Generator, Iterable, Iterator
from datetime import timedelta
from pathlib import Path

import gpstime
import pyarrow
import pyarrow.compute
from arrakis import Channel, Time
from arrakis.block import SeriesBlock, combine_blocks
from arrakis.mux import Muxer
from arrakis_server import errors
from arrakis_server.metadata import ChannelConfigBackend
from arrakis_server.partition import partition_channels
from arrakis_server.scope import Retention, ScopeInfo
from arrakis_server.traits import PublishServerBackend
from confluent_kafka import Consumer, TopicPartition
from platformdirs import user_cache_dir

logger = logging.getLogger("arrakis")

DEFAULT_TIMEOUT = timedelta(seconds=1)


class KafkaBackend(PublishServerBackend):
    """Backend serving timeseries data from Kafka."""

    def __init__(
        self, kafka_url: str, publisher_configs: list[Path] | None, retention_time: int
    ):
        self.kafka_url = kafka_url
        logger.info("kafka URL: %s", self.kafka_url)

        # cache file for self-updating publishers
        # FIXME: how better to manage who can do this
        cache_dir = Path(user_cache_dir("arrakis", "server"))
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = cache_dir / "metadata.toml"
        logger.info("channel cache file: %s", cache_file)

        # load publisher channels
        self.metadata = ChannelConfigBackend(
            cache_file=cache_file,
            enforce=["publisher", "partition_id"],
        )
        if publisher_configs:
            for pconf in publisher_configs:
                logger.info("loading publisher config: %s", pconf)
                added = self.metadata.load(
                    pconf,
                    publisher=pconf.stem,
                    overwrite=False,
                )
                if logger.getEffectiveLevel() <= logging.DEBUG:
                    for channel in added:
                        logger.debug(
                            "  %s: %s %d %s partition_id=%s",
                            channel.publisher,
                            channel.name,
                            channel.sample_rate,
                            channel.dtype,
                            channel.partition_id,
                        )

        self._channels = set(self.metadata.metadata.values())

        retention = Retention(oldest=retention_time)
        self.scope_info = ScopeInfo(self.metadata.scopes, retention)

        # lock used for updating partition table
        self._lock = threading.Lock()

        # Optimize Arrow threading for concurrent client serving
        # single-threaded Arrow operations reduce thread pool contention
        # when serving many concurrent clients
        pyarrow.set_cpu_count(1)

        # Set global memory pool for all Arrow operations across all connections
        optimal_pool = self._get_optimal_memory_pool()
        pyarrow.set_memory_pool(optimal_pool)

    def _get_optimal_memory_pool(self):
        """Select best available memory pool for Arrow operations"""
        # Try high-performance allocators optimized for concurrent workloads
        try:
            pool = pyarrow.jemalloc_memory_pool()
            logger.info("Set jemalloc memory pool for Arrow operations")
            # Set 5 second decay time for dirty/muzzy pages from creation to purge
            # Optimized for batch processing cycles (~100ms) with memory retention
            # see: https://jemalloc.net/jemalloc.3.html#opt.dirty_decay_ms
            pyarrow.jemalloc_set_decay_ms(5000)
            return pool
        except NotImplementedError:
            pass

        try:
            pool = pyarrow.mimalloc_memory_pool()
            logger.info("Set mimalloc memory pool for Arrow operations")
            return pool
        except NotImplementedError:
            pass

        # Fallback to default system pool
        logger.info("Set default memory pool for Arrow operations")
        return pyarrow.default_memory_pool()

    @staticmethod
    def add_arguments(parser):
        parser.add_argument(
            "--kafka-url",
            type=str,
            metavar="URL",
            required=True,
            help="URL pointing to a running kafka pool",
        )
        parser.add_argument(
            "--publisher-config",
            dest="publisher_configs",
            type=Path,
            metavar="PATH",
            action="append",
            help="path to publisher config TOML file or directory",
        )
        parser.add_argument(
            "--retention-time",
            type=int,
            default=900,
            help="Set the data retention stored in Kafka. Default is 900 seconds.",
        )

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> KafkaBackend:
        return cls(
            kafka_url=args.kafka_url,
            publisher_configs=args.publisher_configs,
            retention_time=args.retention_time,
        )

    def find(
        self,
        *,
        pattern: str,
        data_type: list[str],
        min_rate: int,
        max_rate: int,
        publisher: list[str],
    ) -> Iterable[Channel]:
        """Retrieve metadata for the 'find' route."""
        assert isinstance(self.metadata, ChannelConfigBackend)
        return self.metadata.find(
            pattern=pattern,
            data_type=data_type,
            min_rate=min_rate,
            max_rate=max_rate,
            publisher=publisher,
        )

    def describe(self, *, channels: Iterable[str]) -> Iterable[Channel]:
        """Retrieve metadata for the 'find' route."""
        assert isinstance(self.metadata, ChannelConfigBackend)
        return self.metadata.describe(channels=channels)

    def stream(
        self, *, channels: Iterable[str], start: int, end: int
    ) -> Iterator[SeriesBlock]:
        """Retrieve timeseries data for the 'stream' route."""
        assert isinstance(self.metadata, ChannelConfigBackend)
        # query for channel metadata
        metadata = [self.metadata.metadata[channel] for channel in channels]

        if not self.retention.in_range(start) or not self.retention.in_range(end):
            raise errors.TimeRangeUnavailableError(start, end)

        # extract partitions and latency from channels
        partitions = {
            name: channel.partition_id
            for name, channel in self.metadata.metadata.items()
            if channel.partition_id
        }
        max_latency = timedelta(
            seconds=max(
                (
                    channel.expected_latency
                    for channel in self.metadata.metadata.values()
                    if channel.expected_latency is not None
                ),
                default=1,
            )
        )

        # generate live data continuously
        with Connection(self.kafka_url, partitions, metadata) as conn:
            for block in conn.read(start, end, max_latency=max_latency):
                yield block

    def publish(self, *, publisher_id: str) -> dict[str, str]:
        """Retrieve connection info for the 'publish' route."""
        # FIXME: incorporate the producer ID with auth verification
        return {"bootstrap.servers": self.kafka_url}

    def partition(
        self, *, publisher_id: str, channels: Iterable[Channel]
    ) -> Iterable[Channel]:
        assert isinstance(self.metadata, ChannelConfigBackend)

        # assign any new partitions
        changed = set(channels) - self._channels
        if changed:
            partitioned = partition_channels(
                list(changed),
                metadata=self.metadata.metadata,
                partition_metadata=self.metadata.partition_metadata,
                publisher=publisher_id,
            )
            with self._lock:
                self.metadata.update(
                    partitioned,
                    partition_metadata=self.metadata.partition_metadata,
                    overwrite=True,
                )
                self.channels = {channel for channel in self.metadata.metadata.values()}
                # always limit our response to the input list.
                # always send something so that the partition field is set
                channels = [
                    self.metadata.metadata[channel.name] for channel in channels
                ]

        return channels


class Connection:
    """A connection object to read data from Kafka."""

    def __init__(
        self,
        server: str,
        partitions: dict[str, str],
        channels: Iterable[Channel],
    ):
        """Create a Kafka connection.

        Parameters
        ----------
        server : str
            The Kafka broker to connect to.
        channels : Iterable[Channel]
            The channels requested.

        """
        self._channels = set(channels)
        self._channel_map = {channel.name: channel for channel in channels}
        self._partitions = partitions
        # track the indexes that we will use per partition
        self._partition_index_map: dict[str, list[int]] = {}
        # track partition id, index -> channel name
        self._name_lookup: dict[str, dict[int, Channel]] = defaultdict(defaultdict)

        # group channels by partitions
        self._partition_map = defaultdict(list)
        for channel in channels:
            assert channel.partition_id is not None
            assert channel.partition_index is not None
            if channel.name in partitions:
                partition = partitions[channel.name]
                self._partition_map[partition].append(channel.name)
            indexes = self._partition_index_map.get(channel.partition_id, [])
            indexes.append(channel.partition_index)
            self._name_lookup[channel.partition_id][channel.partition_index] = channel
            self._partition_index_map[channel.partition_id] = indexes

        # pre-compute Arrow arrays for filtering to avoid repeated array creation
        self._partition_filter_arrays = {}
        self._partition_filter_sets = {}  # For fast set-based early bailout checks
        self._partition_filter_id_sets = {}
        self._partition_filter_id_arrays = {}
        for partition, channel_names in self._partition_map.items():
            self._partition_filter_arrays[partition] = pyarrow.array(channel_names)
            self._partition_filter_sets[partition] = frozenset(channel_names)
            self._partition_filter_id_arrays[partition] = pyarrow.array(
                self._partition_index_map[partition], type=pyarrow.int32()
            )
            self._partition_filter_id_sets[partition] = frozenset(
                self._partition_index_map[partition]
            )

        # Optimize IPC stream reader creation/destruction overhead
        self._ipc_options = pyarrow.ipc.IpcReadOptions(use_threads=False)

        # create Kafka consumer
        consumer_settings = {
            "bootstrap.servers": server,
            "group.id": generate_groupid(),
            "message.max.bytes": 10_000_000,  # 10 MB
            "enable.auto.commit": False,
        }
        self._consumer = Consumer(consumer_settings)
        self._topics = [
            f"arrakis-{partition}" for partition in self._partition_map.keys()
        ]

    def _smart_filter_batch(
        self, batch: pyarrow.RecordBatch, partition: str
    ) -> pyarrow.RecordBatch:
        """Adaptive filtering with bailout for cases where no filtering is needed."""
        id_column = batch.column("id")

        # get unique channels in this batch
        # this should do anything
        unique_batch_channels = pyarrow.compute.unique(id_column)
        unique_batch_set = set(unique_batch_channels.to_pylist())

        allowed_ids = self._partition_filter_id_sets[partition]

        # check if no unrelated channels are contained in batch
        if unique_batch_set.issubset(allowed_ids):
            return batch

        # keep only rows with requested channels
        mask = pyarrow.compute.is_in(
            id_column,
            self._partition_filter_id_arrays[partition],
        )
        return pyarrow.compute.filter(batch, mask)

    def read(
        self,
        start: int | None = None,
        end: int | None = None,
        max_latency: timedelta = DEFAULT_TIMEOUT,
        poll_timeout: timedelta = DEFAULT_TIMEOUT,
    ) -> Generator[SeriesBlock, None, None]:
        """Read buffers from Kafka. Requires an open connection.

        Parameters
        ----------
        start : numeric, optional
            The GPS time to start receiving buffers for.
            Defaults to 'now'.
        end : numeric, optional
            The GPS time in which to terminate the stream.
            Default is to stream forever.
        max_latency : timedelta, optional
            The maximum latency to wait for messages.
            Default is 1 second.
        poll_timeout : timedelta, optional
            The maximum time to wait for a single message from Kafka.
            Default is 1 second.

        Yields
        ------
        buffers : dict of Buffers, keyed by str
            buffers, keyed by channel name

        """
        logger.debug("creating kafka subscription to topics: %s", self._topics)
        # if start time is specified, adjust the consumer's
        # offset to point at the data requested
        now = int(gpstime.gpsnow() * Time.SECONDS)
        if start and start <= now:
            # convert to UNIX time in ms
            offset_time = int(gpstime.gps2unix(start // Time.SECONDS) * 1000)
            # get offsets corresponding to times
            partitions = [
                TopicPartition(topic, partition=0, offset=offset_time)
                for topic in self._topics
            ]
            partitions = self._consumer.offsets_for_times(partitions)
            # reassign topic partitions to consumer
            self._consumer.unsubscribe()
            self._consumer.assign(partitions)
        else:
            self._consumer.subscribe(self._topics)

        # set up muxer to multiplex buffers
        self._muxer: Muxer[pyarrow.RecordBatch] = Muxer(
            self._partition_map.keys(),
            start=start,
            timeout=max_latency,
        )

        # consume buffers from Kafka
        try:
            while True:
                msg = self._consumer.poll(timeout=poll_timeout.total_seconds())
                if msg and not msg.error():
                    # deserialize message then add to muxer
                    # and pull time-ordered buffers from it
                    partition = msg.topic().split("-", 1)[1]
                    with pyarrow.ipc.open_stream(
                        msg.value(),
                        options=self._ipc_options,
                    ) as reader:
                        for batch_input in read_all_batches(reader):
                            # downselect channels
                            time = batch_input.column("time")[0].as_py()
                            batch = self._smart_filter_batch(batch_input, partition)
                            self._muxer.push(time, partition, batch, on_drop="ignore")

                            # pull muxed blocks and combine
                            for muxed_batch in self._muxer.pull():
                                block = combine_blocks(
                                    *[
                                        SeriesBlock.from_row_batch(
                                            batch,
                                            self._name_lookup[partition],
                                        )
                                        for batch in muxed_batch.values()
                                    ]
                                )

                                # add gaps for missing channels if needed
                                missing = self._channels - set(block.channels.values())
                                if missing:
                                    block = block.create_gaps(missing)

                                # return muxed blocks, handling end condition
                                if end is not None and block.time_ns > end:
                                    return
                                yield block
                                if end is not None and block.time_ns == end:
                                    return

        except Exception as e:
            print(e, file=sys.stderr)

    def __iter__(self) -> Generator[SeriesBlock, None, None]:
        """Read buffers from Kafka. Requires an open connection.

        Calls read() with default parameters.

        """
        yield from self.read()

    def close(self) -> None:
        """Closes a connection to Kafka, unsubscribing from all topics."""
        self._consumer.unassign()
        self._consumer.unsubscribe()
        self._consumer.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def generate_groupid() -> str:
    """Generate a random Kafka group ID."""
    return random_alphanum(16)


def random_alphanum(n: int) -> str:
    """Generate a random alpha-numeric sequence of N characters."""
    alphanum = string.ascii_uppercase + string.digits
    return "".join(random.SystemRandom().choice(alphanum) for _ in range(n))


def read_all_batches(
    reader: pyarrow.ipc.RecordBatchStreamReader,
) -> Iterator[pyarrow.RecordBatch]:
    while True:
        try:
            yield reader.read_next_batch()
        except StopIteration:
            return
