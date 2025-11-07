import time
import logging
from collections.abc import Mapping
from pathlib import PurePosixPath as Path
from blissdata.redis_engine.scan import ScanState
from blissdata.h5map import HDF5ItemType, Group

_logger = logging.getLogger(__name__)


class H5ScanMap(Mapping):
    """H5ScanMap is a wrapper around a blissdata's Scan. It exposes its HDF5
    mapping with conventional dict API, but also handles automatic refresh of
    the underlying model from Redis (see _updated_root method).

    IMPORTANT: This is not an H5-like object, it helps manipulating the mapping
    within a scan. Then H5-like groups and datasets can be implemented on top of
    it."""

    def __init__(self, scan):
        self._scan = scan
        self._root = None
        self._last_update = time.perf_counter()

    @property
    def scan(self):
        return self._scan

    def __len__(self):
        return len(self._updated_root().children)

    def __iter__(self):
        yield from self._updated_root().children.keys()

    def __getitem__(self, path: str) -> HDF5ItemType:
        """Return the HDF5Item associated to that path.
        Links are not resolved here, instead a SoftLink or ExternalLink is
        returned and it is caller choice to resolve it or not.
        """
        assert path.startswith("/")
        h5_item = self._updated_root()
        current_path = Path("/")
        for part in Path(path).parts:
            if part == "/":
                continue
            current_path /= part
            if not isinstance(h5_item, Group):
                raise KeyError(str(current_path))
            try:
                h5_item = h5_item.children[part]
            except KeyError:
                raise KeyError(str(current_path))
        return h5_item

    def path_partition(self, path: str) -> tuple[str, HDF5ItemType | None, str]:
        """Similar to __getitem__, but may return partially resolved path.
        Goal is to allow link items to be returned along with the remaining
        part of the path. Links can be resolved before going further.

        Returns:
            tuple:
                - path of the returned item
                - h5map item or None if path doesn't exist
                - remaining path (empty if item is the actual target)

        Example:
            /
            ├─a
            │ ├─b (link to d)
            │ └─c
            └─d
              └─e

           path_partition("/a/b/c") -> "/a/b/c", Dataset(...), ""
           path_partition("/a/b/e") -> "/a/b", SoftLink("/d"), "e"
           path_partition("/a/x/y") -> "/a/x", None, "y"
        """
        assert path.startswith("/")
        h5_item = self._updated_root()
        item_parts = ["/"]
        remaining_parts = list(Path(path).parts[1:])
        while remaining_parts:
            if isinstance(h5_item, Group):
                try:
                    item_parts.append(remaining_parts.pop(0))
                    h5_item = h5_item.children[item_parts[-1]]
                except KeyError:
                    h5_item = None
                    break
            else:
                break
        remaining_path = str(Path(*remaining_parts)) if remaining_parts else ""
        return str(Path(*item_parts)), h5_item, remaining_path

    def _updated_root(self) -> Group:
        """Return an h5map.Group loaded from scan info. Reuse previous answer if
        not older than 0.2 seconds (polling Redis to 5Hz at most if fine).
        Moreover, scan state doesn't change that much and the scan's json is
        only downloaded on changes.

        In case the scan provides no mapping, an empty Group is returned.
        """
        scan_state_changed = False

        # Mapping is not expected to be published before scan is prepared, wait
        while self._scan.state < ScanState.PREPARED:
            self._scan.update()
            self._last_update = time.perf_counter()
            scan_state_changed = True

        # Update whenever the scan is not CLOSED and the last_update is not too
        # recent.
        min_update_interval = 0.2
        now = time.perf_counter()
        if (
            self._last_update + min_update_interval < now
            and self._scan.state < ScanState.CLOSED
        ):
            scan_state_changed = self._scan.update(block=False)
            self._last_update = time.perf_counter()

        # (re)generate mapping tree if necessary
        if scan_state_changed or self._root is None:
            try:
                mappings = self._scan.info.get("h5maps", {})
                self._root = Group.model_validate(mappings[self._scan.path])
            except KeyError:
                _logger.warning(
                    f"Scan {self._scan.number} has no hdf5 mapping ({self._scan.key})"
                )
                return Group()

        return self._root
