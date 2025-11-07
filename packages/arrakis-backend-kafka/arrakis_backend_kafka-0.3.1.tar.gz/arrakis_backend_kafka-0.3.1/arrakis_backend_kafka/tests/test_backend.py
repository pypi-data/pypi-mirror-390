from collections import namedtuple
from unittest.mock import patch

import pyarrow
from arrakis import Channel

from arrakis_backend_kafka import backend

DummyChannel = namedtuple("DummyChannel", ["name", "partition_id", "partition_index"])


def build_test_rb1() -> pyarrow.RecordBatch:
    time = [1000, 1000]
    ids = pyarrow.array([42, 5], type=pyarrow.uint32())
    data = [
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
        [
            2,
        ],
    ]

    names = ["time", "id", "data"]
    return pyarrow.RecordBatch.from_arrays([time, ids, data], names=names)


def build_test_rb1_with_extra() -> pyarrow.RecordBatch:
    time = [1000, 1000, 1000, 1000]
    ids = pyarrow.array([42, 43, 5, 6], type=pyarrow.uint32())
    data = [
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
        [43],
        [
            2,
        ],
        [6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
    ]

    names = ["time", "id", "data"]
    return pyarrow.RecordBatch.from_arrays([time, ids, data], names=names)


def build_rb1_channels() -> list[Channel]:
    return [
        Channel(
            name="X1:TST-SUB_1",
            data_type="int64",
            sample_rate=256,
            partition_id="PART1",
            partition_index=42,
        ),
        Channel(
            name="X1:TST-SUB_2",
            data_type="int64",
            sample_rate=16,
            partition_id="PART1",
            partition_index=5,
        ),
    ]


def build_rb1_partition_mapping() -> dict[str, str]:
    return {
        "X1:TST-SUB_1": "PART1",
        "X1:TST-SUB_1A": "PART1",
        "X1:TST-SUB_2": "PART1",
        "X1:TST-SUB_2A": "PART1",
    }


def test_smart_filter_batch_fast():
    input = build_test_rb1()
    expected_output = build_test_rb1()
    partition = "PART1"
    partitions = build_rb1_partition_mapping()
    channels = build_rb1_channels()

    with patch("confluent_kafka.Consumer"):
        conn = backend.Connection(
            server="grpc://non-existant:31206",
            partitions=partitions,
            channels=channels,
        )

        actual = conn._smart_filter_batch(input, partition)
    assert actual == expected_output


def test_smart_filter_batch():
    input = build_test_rb1_with_extra()
    expected_output = build_test_rb1()
    partition = "PART1"
    partitions = build_rb1_partition_mapping()
    channels = build_rb1_channels()

    conn = backend.Connection(
        server="grpc://non-existant:31206",
        partitions=partitions,
        channels=channels,
    )

    actual = conn._smart_filter_batch(input, partition)
    assert actual == expected_output
