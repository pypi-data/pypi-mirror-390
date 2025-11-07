import re
import time
import math
import functools
import numpy as np
from abc import ABC, abstractmethod
from pathlib import PurePosixPath as Path

import blissdata.h5map as h5m
from blissdata.beacon.data import BeaconData
from blissdata.redis_engine.store import DataStore
from blissdata.redis_engine.exceptions import EndOfStream, IndexNotYetThereError
from blissdata.h5api import abstract
from blissdata.h5api.h5_scan_map import H5ScanMap


class Attributes(abstract.Attributes):
    def __init__(self, dct):
        self.dct = dct
        super().__init__()

    def __repr__(self):
        return f"<Attributes of Redis-HDF5 object at {hex(id(self))}>"

    def __getitem__(self, key: str):
        return self.dct[key]

    def __iter__(self):
        yield from self.dct

    def __len__(self):
        return len(self.dct)


class File(abstract.File):
    """This File class mimics the h5py API without an actual file, instead it
    exposes data from Redis directly by relying on Scans and Streams. It means
    file can iterate on live data.
    """

    def __init__(
        self, filepath: str, mode: str = "r", data_store: DataStore | None = None
    ):
        """If no data_store is provided, but $BEACON_HOST variable is defined,
        then try to query Redis address from that beacon server."""
        if mode != "r":
            raise ValueError("Invalid mode; only r is supported with live mode")
        self._filepath = Path(filepath)
        self._closed = False
        if data_store is None:
            try:
                beacon = BeaconData()
            except ValueError as e:
                raise ValueError(
                    f"No DataStore provided, but cannot ask beacon server neither: {e}"
                ) from None
            self._data_store = DataStore(beacon.get_redis_data_db())
        else:
            self._data_store = data_store

    @property
    def name(self) -> str:
        return "/"

    @property
    def filename(self) -> str:
        return str(self._filepath)

    @property
    def attrs(self) -> abstract.Attributes:
        return Attributes({"NX_class": "NXroot"})

    @property
    def file(self) -> "File":
        return self

    @property
    def parent(self) -> "Group":
        return self["/"]

    def close(self):
        self._closed = True

    def __repr__(self):
        return f'<Live-HDF5 file "{self._filepath.name}" (mode r)>'

    def __len__(self):
        """Return the instant length from the scans that are already there."""
        return len(self.keys())

    def __getitem__(self, path: str):
        # save originally requested path
        original_path = path

        # track visited paths to detect link cycles
        visited_paths = []
        while path:
            path = Path("/") / path
            if str(path) in visited_paths:
                raise KeyError(
                    f"'{original_path}': path can't be resolved, found link cycle: {[str(p) for p in visited_paths]}"
                )
            else:
                visited_paths.append(str(path))

            scan_path = self._scan_path(path)
            if scan_path == "/":
                return Group(self, "/", self.attrs)

            try:
                scan_map = self._get_scan_map_by_path(scan_path)
            except KeyError:
                raise KeyError(f"No such path: '{scan_path}'")

            item_path, item, remain_path = scan_map.path_partition(str(path))
            if item is None:
                raise KeyError(f"No such path: '{item_path}'")

            if isinstance(item, h5m.SoftLink):
                path = Path(item_path).parent / item.target_path / remain_path
            elif isinstance(item, h5m.ExternalLink):
                # NOTE no protection against link cycles involving multiple files
                return File(item.target_file, data_store=self._data_store)[
                    str(Path(item.target_path) / remain_path)
                ]
            elif remain_path:
                raise KeyError(
                    f"'{item_path}' is not a Group, can't reach '{str(path)}'"
                )
            else:
                return self._map_item_to_h5(str(path), item, scan_map.scan)

    def _map_item_to_h5(self, path: str, item: h5m.HDF5ItemType, scan):
        if isinstance(item, h5m.Group):
            return Group(self, path, item.attributes)
        elif isinstance(
            item, (h5m.Dataset, h5m.ExternalBinaryDataset, h5m.VirtualDataset)
        ):
            return dataset_factory(self, path, item, scan)
        elif isinstance(item, h5m.SoftLink):
            raise TypeError("Oops, unresolved h5m.SoftLink should not end up there")
        elif isinstance(item, h5m.ExternalLink):
            raise TypeError("Oops, unresolved h5m.ExternalLink should not end up there")
        else:
            raise TypeError(f"Unknown item type {type(item).__name__}")

    def __iter__(self) -> str:
        """Iterate forever: keep waiting for new scans once existing ones are
        yielded."""
        # iterate through existing scans in that file_path
        ts, keys = self._data_store.search_existing_scans(path=self.filename)
        for key in keys:
            yield from self._get_scan_map_by_key(key)

        # iterate forever over the next scans
        while True:
            ts, key = self._data_store.get_next_scan(since=ts)
            # Note: Read a single json attribute without loading the scan,
            # this requires to know the json model and should not be used
            # outside of blissdata (a proper API should be discussed if needed)
            path = self._data_store._redis.json().get(key, "id.path")
            if path == self.filename:
                yield from self._get_scan_map_by_key(key)

    def keys(self):
        """Instant list of keys in the file. Can be used to only iterate over
        existing scans without blocking then."""
        _, keys = self._data_store.search_existing_scans(path=self.filename)
        ret = set()
        for key in keys:
            ret |= set(self._get_scan_map_by_key(key).keys())
        return ret

    def _get_scan_map_by_path(self, scan_path: str) -> H5ScanMap:
        key = self._get_scan_key(scan_path)
        return self._get_scan_map_by_key(key)

    def _get_scan_key(self, scan_path: str) -> str:
        return File._get_scan_key_cached(self._data_store, self.filename, scan_path)

    @staticmethod
    @functools.lru_cache(maxsize=100)
    def _get_scan_key_cached(
        data_store: DataStore, filename: str, scan_path: str
    ) -> str:
        if not re.fullmatch("/[0-9]*.[0-9]+", scan_path):
            raise KeyError(f"No such path: {scan_path}")
        scan_number = int(scan_path[1:].split(".")[0])
        _, keys = data_store.search_existing_scans(path=filename, number=scan_number)
        if len(keys) != 1:
            if not keys:
                # WARNING could be in file and not in Redis anymore...
                raise KeyError(f"No such scan number: {scan_number}")
            else:
                raise RuntimeError(
                    f"Found multiple scans number {scan_number} in {filename}: {keys}"
                )
        return keys.pop()

    def _get_scan_map_by_key(self, key: str) -> H5ScanMap:
        """Load a scan from Redis, wrap it into a H5ScanMap and update
        cache"""
        return File._get_scan_map_by_key_cached(self._data_store, key)

    @staticmethod
    @functools.lru_cache(maxsize=100)
    def _get_scan_map_by_key_cached(data_store: DataStore, key: str) -> H5ScanMap:
        scan = data_store.load_scan(key)
        return H5ScanMap(scan)

    def _len_group(self, path: str) -> int:
        """Used by Group.__len__ to query length of a particular path (not only
        the root)"""
        scan_path = self._scan_path(path)
        if scan_path == "/":
            return len(self)
        else:
            # number of items inside a scan
            try:
                scan_map = self._get_scan_map_by_path(scan_path)
                group_item = scan_map[path]
            except KeyError as e:
                raise KeyError(f"No such path: {str(scan_path / e.args[0])}")
            return len(group_item.children)

    def _iter_group(self, path: str) -> str:
        """Used by Group.__iter__ to iterate through a particular path (not
        only the root)."""
        scan_path = self._scan_path(path)
        if scan_path == "/":
            # iterate over scans (never stops)
            yield from self
        else:
            # iterate inside a scan
            try:
                scan_map = self._get_scan_map_by_path(scan_path)
                group_item = scan_map[path]
            except KeyError as e:
                raise KeyError(f"No such path: {str(scan_path / e.args[0])}")
            yield from group_item.children

    def _scan_path(self, path: str) -> str:
        """Make path canonical and keep scan part only
        ''             -> '/',
        '123.1'        -> '/123.1',
        '//123.1///'   -> '/123.1',
        '/123.1/a/b/c' -> '/123.1',
        """
        path = Path("/") / path
        if len(path.parts) <= 2:
            return str(path)
        else:
            return str(Path(*path.parts[:2]))


class Node(abstract.Node):
    def __init__(
        self,
        file: File,
        path: str,
        attrs: dict,
    ):
        self._file = file
        self._path = path
        self._attrs = attrs

    @property
    def name(self):
        return self._path

    @property
    def attrs(self):
        return Attributes(self._attrs)

    @property
    def file(self):
        return self._file

    @property
    def parent(self):
        parent_path = Path(self._path).parent
        return self._file[str(parent_path)]


class Group(Node, abstract.Group):
    def __init__(
        self,
        file: File,
        path: str,
        attrs: dict,
    ):
        assert path.startswith("/")
        Node.__init__(self, file, path, attrs)

    @property
    def name(self):
        return self._path

    def __repr__(self):
        try:
            length = len(self)
        except Exception:
            length = "?"
        return f'<Live-HDF5 group "{self._path}" ({length} members)>'

    def __getitem__(self, path: str):
        try:
            return self._file[str(self._path / Path(path))]
        except TypeError:
            raise TypeError(
                f"Accessing a group is done with bytes or str, not {type(path)}"
            )

    def __iter__(self):
        yield from self._file._iter_group(self._path)

    def __len__(self):
        return self._file._len_group(self._path)


class Dataset(Node, abstract.Dataset):
    def __init__(
        self,
        file: File,
        path: str,
        attrs: dict,
        array: ...,
        virtual: bool = False,
        external=None,
    ):
        Node.__init__(self, file, path, attrs)
        self._array = array
        self._virtual = virtual
        self._external = external

    def __repr__(self):
        if isinstance(self._array, StreamAsArray):
            shape = f"(_,{','.join([str(i) for i in self._array._stream.shape])})"
        else:
            shape = self.shape
        return f'<Live-HDF5 dataset "{Path(self.name).name}": shape {shape}, type "{self.dtype.str}">'

    @property
    def is_virtual(self):
        return self._virtual

    @property
    def external(self):
        return self._external

    def __getitem__(self, idx):
        if self.ndim == 0 and idx != ():
            raise ValueError("Illegal slicing argument for scalar dataspace")
        return self._array[idx]

    def __len__(self):
        if self.ndim == 0:
            raise TypeError("Attempt to take len() of scalar dataset")
        return len(self._array)

    @property
    def dtype(self):
        return self._array.dtype

    @property
    def shape(self):
        return self._array.shape

    @property
    def ndim(self):
        return self._array.ndim

    @property
    def size(self):
        return self._array.size

    def __iter__(self):
        if self.ndim == 0:
            raise TypeError("Can't iterate over a scalar dataset")
        yield from self._array


class ArrayInterface(ABC):
    @abstractmethod
    def __getitem__(self, idx):
        pass

    @abstractmethod
    def __len__(self):
        pass

    @property
    @abstractmethod
    def dtype(self):
        pass

    @property
    @abstractmethod
    def shape(self):
        pass

    @property
    @abstractmethod
    def ndim(self):
        pass

    @property
    @abstractmethod
    def size(self):
        pass

    @abstractmethod
    def __iter__(self):
        pass


class StreamAsArray(ArrayInterface):
    def __init__(self, stream):
        assert stream.kind == "array"
        self._stream = stream

    def __getitem__(self, idx):
        if isinstance(idx, int):
            if idx < 0:
                self._stream.wait_seal()
                return self._stream[idx]
            else:
                while True:
                    try:
                        return self._stream[idx]
                    except IndexNotYetThereError:
                        time.sleep(0.5)
        elif isinstance(idx, slice):
            if idx.stop is None or idx.stop < 0:
                self._stream.wait_seal()
                return self._stream[idx]
            else:
                while len(self._stream) < idx.stop and not self._stream.is_sealed():
                    time.sleep(0.5)
                return self._stream[idx]
        elif isinstance(idx, tuple):
            if idx == ():
                return self._stream[:]
            else:
                raise NotImplementedError

    def __len__(self):
        return len(self._stream)

    @property
    def dtype(self):
        return self._stream.dtype

    @property
    def shape(self):
        return (len(self),) + self._stream.shape

    @property
    def ndim(self):
        return len(self._stream.shape) + 1

    @property
    def size(self):
        return math.prod(self.shape)

    def __iter__(self):
        cursor = self._stream.cursor()
        while True:
            try:
                view = cursor.read()
                yield from view
            except EndOfStream:
                break


class ExternalBinaryAsArray:
    def __init__(self, item):
        self.memmaps = []
        self._shape = tuple(item.shape)
        self._dtype = np.dtype(item.dtype)
        for file in item.files:
            if file.size is None:
                shape = None
            else:
                shape = (file.size // self._dtype.itemsize,)
            self.memmaps.append(
                np.memmap(
                    file.name,
                    dtype=self._dtype,
                    mode="r",
                    offset=file.offset,
                    shape=shape,
                )
            )

        # NOTE naive approach loading files in memory, but memmaps could be
        # accessed on demand
        self._data = np.concatenate([m for m in self.memmaps])[: self.size].reshape(
            self.shape
        )

    def __getitem__(self, key):
        return self._data[key]

    def __len__(self):
        return self._shape[0]

    @property
    def dtype(self):
        return self._dtype

    @property
    def shape(self):
        return self._shape

    @property
    def ndim(self):
        return len(self._shape)

    @property
    def size(self):
        return math.prod(self._shape)

    def __iter__(self):
        yield from self._data


def dataset_factory(parent: File, path: str, item: h5m.HDF5ItemType, scan) -> Dataset:
    virtual = False
    external = None
    if isinstance(item, h5m.Dataset):
        if isinstance(item.value, h5m.Stream):
            array = StreamAsArray(scan.streams[item.value.stream])
        else:
            array = item.value.decode()
    elif isinstance(item, h5m.ExternalBinaryDataset):
        external = [(file.name, file.offset, file.size) for file in item.files]
        array = ExternalBinaryAsArray(item)
    elif isinstance(item, h5m.VirtualDataset):
        virtual = True
        # TODO
        raise NotImplementedError

    return Dataset(parent, path, item, array, virtual, external)
