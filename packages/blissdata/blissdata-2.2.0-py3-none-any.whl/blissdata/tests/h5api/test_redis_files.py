import pytest
import h5py
import threading
import time
import numpy as np
from blissdata.streams.base import Stream
from blissdata.h5api.redis_hdf5 import File, Group
import blissdata.h5map as h5m


def build_scan(data_store, number, path):
    return data_store.create_scan(
        identity={
            "name": "generated_scan",
            "number": number,
            "data_policy": "None",
            "path": path,
        },
    )


def test_file_open():
    with pytest.raises(ValueError) as exc_info:
        _ = File("dummy_path")
    assert "No DataStore provided" in str(exc_info)
    assert "$BEACON_HOST is not specified" in str(exc_info)


@pytest.mark.timeout(30)
def test_file_iter(data_store, tmpdir):
    file_path = str(tmpdir / "data.h5")
    file = File(file_path, data_store=data_store)
    assert len(file) == 0

    # listen for three scans in a thread
    def iter_over_three_scans(keys: list):
        for key in file:
            keys.append(key)
            assert key == f"{len(keys)}.1"
            if len(keys) == 3:
                break

    keys = []
    t = threading.Thread(target=iter_over_three_scans, args=(keys,))
    t.start()

    # run three scans
    for i in range(3):
        scan = build_scan(data_store, i + 1, file_path)
        scan.info["h5maps"] = {
            file_path: h5m.Group(children={f"{i + 1}.1": h5m.Group()}).model_dump()
        }
        scan.close()

    # ensure the iterator got them all
    t.join()
    assert len(keys) == 3
    assert len(file) == 3


def test_file_getitem(data_store, tmpdir):
    file_path = str(tmpdir / "data.h5")
    file = File(file_path, data_store=data_store)

    # no such scan
    with pytest.raises(KeyError):
        _ = file["1.1"]

    scan = build_scan(data_store, 1, file_path)
    scan.info["h5maps"] = {
        file_path: h5m.Group(children={"1.1": h5m.Group()}).model_dump()
    }

    scan.prepare()

    # scan found
    group = file["1.1"]
    assert isinstance(group, Group)

    _ = build_scan(data_store, 2, str(tmpdir / "another_file.h5"))

    # Scan 2 not in that file
    with pytest.raises(KeyError):
        _ = file["2.1"]


def test_missing_scan_mapping(data_store, tmpdir):
    file_path = str(tmpdir / "data.h5")
    file = File(file_path, data_store=data_store)

    scan = build_scan(data_store, 1, file_path)
    scan.prepare()

    with pytest.raises(KeyError):
        _ = file["1.1"]


def test_scan_iter(data_store, tmpdir):
    file_path = str(tmpdir / "data.h5")
    file = File(file_path, data_store=data_store)

    scan = build_scan(data_store, 1, file_path)
    mapping = h5m.Group(
        children={
            "1.1": h5m.Group(
                children={
                    "abc": h5m.Group(),
                    "def": h5m.Group(),
                    "ghi": h5m.Group(),
                }
            )
        }
    )
    scan.info["h5maps"] = {file_path: mapping.model_dump()}

    scan.prepare()

    assert set(file[f"{scan.number}.1"]) == {"abc", "def", "ghi"}


def test_scan_getitem(data_store, tmpdir):
    file_path = str(tmpdir / "data.h5")
    file = File(file_path, data_store=data_store)

    scan = build_scan(data_store, 1, file_path)
    mapping = h5m.Group(
        children={
            "1.1": h5m.Group(
                children={
                    "abc": h5m.Group(
                        children={"def": h5m.Group(children={"ghi": h5m.Group()})}
                    ),
                    "xyz": h5m.Group(),
                    "dset": h5m.Dataset(value=3),
                }
            )
        }
    )
    scan.info["h5maps"] = {file_path: mapping.model_dump()}

    scan.prepare()

    group = file[f"{scan.number}.1"]
    assert len(group) == 3

    test_path = f"/{scan.number}.1/abc/def/ghi"
    assert group["abc/def/ghi"].name == test_path
    assert group["abc"]["def"]["ghi"].name == test_path
    assert group[f"/{scan.number}.1/abc/def/ghi"].name == test_path
    assert file[f"/{scan.number}.1/abc/def/ghi"].name == test_path

    with pytest.raises(KeyError) as exc_info:
        group["abc/ERR/def/ghi"]
    assert exc_info.value.args[0] == "No such path: '/1.1/abc/ERR'"

    with pytest.raises(KeyError) as exc_info:
        group["dset/none"]
    assert (
        exc_info.value.args[0]
        == "'/1.1/dset' is not a Group, can't reach '/1.1/dset/none'"
    )

    # edit mapping on scan closing
    scan.start()
    scan.stop()

    mapping.children["1.1"].children["xyz"].children["uvw"] = h5m.Group()
    scan.info["h5maps"][file_path] = mapping.model_dump()
    scan.close()

    # try to access new group until available
    start = time.perf_counter()
    while True:
        try:
            _ = group[f"/{scan.number}.1/xyz/uvw"]
            break
        except KeyError:
            if time.perf_counter() < start + 5:
                time.sleep(0.05)
            else:
                raise


def test_soft_link(data_store, tmpdir):
    file_path = str(tmpdir / "data.h5")
    file = File(file_path, data_store=data_store)
    scan = build_scan(data_store, 1, file_path)
    mapping = h5m.Group(
        children={
            "1.1": h5m.Group(
                children={
                    "abs": h5m.SoftLink(target_path="/1.1/target"),
                    "rel": h5m.SoftLink(target_path="target"),
                    "data_link": h5m.SoftLink(target_path="/1.1/target/data"),
                    "target": h5m.Group(
                        children={
                            "x": h5m.Group(children={"y": h5m.Group()}),
                            "data": h5m.Dataset(value=123.456),
                            "cycle2": h5m.SoftLink(target_path="/1.1/cycle1"),
                            "broken": h5m.SoftLink(target_path="/1.1/pipeau"),
                        }
                    ),
                    "cycle1": h5m.SoftLink(target_path="/1.1/abs/cycle2"),
                }
            )
        }
    )
    scan.info["h5maps"] = {file_path: mapping.model_dump()}
    scan.prepare()

    # path up to link
    assert file["/1.1/abs"].name == "/1.1/target"
    assert file["/1.1/rel"].name == "/1.1/target"

    # path further link
    assert file["/1.1/abs/x/y"].name == "/1.1/target/x/y"
    assert file["/1.1/rel/x/y"].name == "/1.1/target/x/y"

    # link to dataset
    assert file["/1.1/data_link"][()] == 123.456

    # link cycle
    with pytest.raises(KeyError) as exc_info:
        _ = file["/1.1/cycle1"]
    assert "found link cycle" in str(exc_info)

    # broken link
    with pytest.raises(KeyError):
        _ = file["/1.1/target/broken"]


def test_soft_link_outside_scan(data_store, tmpdir):
    file_path = str(tmpdir / "data.h5")
    file = File(file_path, data_store=data_store)
    scan = build_scan(data_store, 1, file_path)
    mapping = h5m.Group(
        children={
            "1.1": h5m.Group(
                children={
                    "target": h5m.Dataset(value=42),
                }
            )
        }
    )
    scan.info["h5maps"] = {file_path: mapping.model_dump()}
    scan.close()

    scan = build_scan(data_store, 2, file_path)
    mapping = h5m.Group(
        children={
            "2.1": h5m.Group(
                children={
                    "link_to_another_scan": h5m.SoftLink(target_path="/1.1/target"),
                }
            )
        }
    )
    scan.info["h5maps"] = {file_path: mapping.model_dump()}
    scan.close()

    assert file["/2.1/link_to_another_scan"][()] == 42


def test_external_link(data_store, tmpdir):
    alt_file_path = str(tmpdir / "alt_data.h5")
    scan = build_scan(data_store, 1, alt_file_path)
    mapping = h5m.Group(
        children={
            "1.1": h5m.Group(
                children={
                    "target": h5m.Dataset(value=42),
                }
            )
        }
    )
    scan.info["h5maps"] = {alt_file_path: mapping.model_dump()}
    scan.close()

    file_path = str(tmpdir / "data.h5")
    file = File(file_path, data_store=data_store)
    scan = build_scan(data_store, 2, file_path)
    mapping = h5m.Group(
        children={
            "2.1": h5m.Group(
                children={
                    "link_to_another_file": h5m.ExternalLink(
                        target_file=alt_file_path, target_path="/1.1/target"
                    ),
                }
            )
        }
    )
    scan.info["h5maps"] = {file_path: mapping.model_dump()}
    scan.close()

    assert file["/2.1/link_to_another_file"][()] == 42


@pytest.mark.parametrize(
    "value",
    [
        h5m.InlineRaw(3),
        h5m.InlineRaw([1, 2, 3]),
        h5m.InlineRaw([[1, 2], [3, 4]]),
        h5m.InlineRaw("hello"),
        h5m.InlineRaw("🃏"),
        h5m.InlineRaw(["a", "b", "c"]),
        h5m.Inline(value=1.23, dtype="float16"),
        h5m.Inline(value=[1.23, "4.56"], dtype="float32"),
    ],
)
def test_static_dataset(data_store, tmpdir, value):
    file_path = str(tmpdir / "data.h5")
    file = File(file_path, data_store=data_store)
    scan = build_scan(data_store, 1, file_path)
    mapping = h5m.Group(children={"1.1": h5m.Group(children={"dset": value})})
    scan.info["h5maps"] = {file_path: mapping.model_dump()}
    scan.close()

    dset = file[f"/{scan.number}.1/dset"]

    expected = value.decode()
    assert np.array_equal(dset[()], expected[()])
    assert dset.dtype == expected.dtype
    assert dset.shape == expected.shape
    assert dset.ndim == expected.ndim
    assert dset.size == expected.size
    assert dset.is_virtual is False
    assert dset.external is None

    if expected.shape:
        assert len(dset) == len(expected)
        assert np.array_equal(list(dset), list(expected))
    else:
        with pytest.raises(Exception):
            len(dset)
        with pytest.raises(Exception):
            list(dset)


@pytest.mark.parametrize(
    "data, dtype, shape",
    [
        (np.arange(20, dtype=np.int16), np.int16, ()),
        (np.arange(60, dtype=np.float64).reshape((10, 2, 3)), np.float64, (2, 3)),
    ],
)
def test_stream_dataset(data_store, tmpdir, data, dtype, shape):
    file_path = str(tmpdir / "data.h5")
    file = File(file_path, data_store=data_store)
    scan = build_scan(data_store, 1, file_path)
    stream_definition = Stream.make_definition("mystream", dtype, shape)
    stream = scan.create_stream(stream_definition)
    mapping = h5m.Group(
        children={
            "1.1": h5m.Group(
                children={
                    "dset": h5m.Stream(stream="mystream"),
                }
            )
        }
    )
    scan.info["h5maps"] = {file_path: mapping.model_dump()}
    scan.prepare()
    scan.start()
    stream.send(data[0])
    stream.send(data[1:5])
    stream.send(data[5:])
    scan.close()

    dset = file[f"/{scan.number}.1/dset"]

    assert np.array_equal(dset[()], data[()])
    assert dset.dtype == dtype
    assert dset.shape == data.shape
    assert dset.ndim == data.ndim
    assert dset.size == data.size
    assert dset.is_virtual is False
    assert dset.external is None
    assert len(dset) == len(data)
    assert np.array_equal(list(dset), list(data))


@pytest.mark.parametrize(
    "dtype, shape, ext_files",
    [
        (
            "|u1",
            (100,),
            [
                ("dat0.bin", 123, 100),
            ],
        ),
        (
            "<i8",
            (100,),
            [
                ("dat0.bin", 8, 240),
                ("dat1.bin", 160, 560),
            ],
        ),
        (
            ">f2",
            (5, 60),
            [
                ("dat0.bin", 400, 200),
                ("dat1.bin", 12, 400),
            ],
        ),
        (
            "<u2",
            (7, 120),
            [
                ("dat0.bin", 14, 280),
                ("dat1.bin", 0, None),
            ],
        ),
    ],
)
def test_external_binary_dataset(data_store, tmpdir, dtype, shape, ext_files):
    file_path = str(tmpdir / "data.h5")
    ref_file_path = str(tmpdir / "ref_file.h5")
    file = File(file_path, data_store=data_store)
    scan = build_scan(data_store, 1, file_path)

    # prefix files path with test dir
    ext_files = [(str(tmpdir / f[0]), f[1], f[2]) for f in ext_files]

    for name, offset, size in ext_files:
        # create binary files with fake data
        if size is None:
            size = 6000
        data = (
            np.random.rand((offset + size) // np.dtype(dtype).itemsize) * 1000
        ).astype(dtype)
        data.tofile(name)

    # create a real hdf5 external binary dataset as reference
    with h5py.File(ref_file_path, "w") as f:
        f.create_group("1.1").create_dataset(
            name="dset",
            dtype=dtype,
            shape=shape,
            external=[
                tuple(f) if f[2] is not None else (f[0], f[1], h5py.h5f.UNLIMITED)
                for f in ext_files
            ],
        )

    mapping = h5m.Group(
        children={
            "1.1": h5m.Group(
                children={
                    "dset": h5m.ExternalBinaryDataset(
                        dtype=dtype,
                        shape=shape,
                        files=[
                            {"name": f[0], "offset": f[1], "size": f[2]}
                            for f in ext_files
                        ],
                    ),
                }
            )
        }
    )
    scan.info["h5maps"] = {file_path: mapping.model_dump()}
    scan.close()

    with h5py.File(str(tmpdir / "ref_file.h5"), "r") as f:
        ref_dset = f["/1.1/dset"]
        dset = file[f"/{scan.number}.1/dset"]
        assert np.array_equal(dset[()], ref_dset[()])
        assert dset.dtype == ref_dset.dtype
        assert dset.shape == ref_dset.shape
        assert dset.ndim == ref_dset.ndim
        assert dset.size == ref_dset.size
        assert dset.is_virtual is False
        assert dset.external == ext_files
        assert len(dset) == len(ref_dset)
        assert np.array_equal(list(dset), list(ref_dset))


@pytest.mark.skip(reason="TODO")
def test_virtual_dataset(data_store, tmpdir):
    raise NotImplementedError
