import pytest
import numpy as np
from contextlib import contextmanager
import blissdata.redis_engine.scan
from blissdata.redis_engine.exceptions import MissingPluginException
from blissdata.streams.base import (
    Stream,
    StreamDefinition,
    View,
    EventRange,
    BrokenPluginStream,
    MissingPluginStream,
)


class FakePluginView(View):
    pass


class FakePluginStream(Stream):
    def __init__(self, event_stream):
        if event_stream.info.get("fail", False):
            raise Exception("Oops, broken plugin...")
        super().__init__(event_stream)

    @staticmethod
    def make_definition(name, info={}) -> StreamDefinition:
        return Stream.make_definition(
            name, dtype=np.int64, info=info | {"plugin": "fake"}
        )

    @property
    def kind(self):
        return "fake"

    @property
    def plugin(self):
        return "fake"

    def _build_view_from_events(self, index, events: EventRange, last_only):
        return FakePluginView(events)


@contextmanager
def fake_plugin_available():
    """Emulate installation of 'fake' plugin module"""

    class FakePluginModule:
        stream_cls = FakePluginStream
        view_cls = FakePluginView

    plugin_modules = blissdata.redis_engine.scan.loaded_plugins
    try:
        plugin_modules["fake"] = FakePluginModule
        yield
    finally:
        del plugin_modules["fake"]


def test_plugin_load(dummy_scan):
    with fake_plugin_available():
        stream_definition = FakePluginStream.make_definition("mystream")
        _ = dummy_scan.create_stream(stream_definition)
        dummy_scan.prepare()

        stream = dummy_scan.streams["mystream"]
        assert isinstance(stream, FakePluginStream)


def test_missing_plugin_create(dummy_scan):
    stream_definition = FakePluginStream.make_definition("mystream")
    with pytest.raises(MissingPluginException):
        _ = dummy_scan.create_stream(stream_definition)


def test_missing_plugin_load(dummy_scan):
    with fake_plugin_available():
        stream_definition = FakePluginStream.make_definition("mystream")
        _ = dummy_scan.create_stream(stream_definition)
    dummy_scan.prepare()
    stream = dummy_scan.streams["mystream"]
    assert isinstance(stream, MissingPluginStream)
    with pytest.raises(MissingPluginException):
        len(stream)


def test_broken_plugin_create(data_store, dummy_scan):
    with fake_plugin_available():
        stream_definition = FakePluginStream.make_definition(
            "mystream", info={"fail": True}
        )
        with pytest.raises(Exception) as exc_info:
            _ = dummy_scan.create_stream(stream_definition)
        assert "Oops, broken plugin..." in str(exc_info)


def test_broken_plugin_load(data_store, dummy_scan):
    with fake_plugin_available():
        stream_definition = FakePluginStream.make_definition(
            "mystream", info={"fail": False}
        )
        rw_stream = dummy_scan.create_stream(stream_definition)

        # manually patch stream info after creation, but before publishing json
        rw_stream._event_stream._model.info["fail"] = True
        dummy_scan.prepare()

        stream = dummy_scan.streams["mystream"]
        assert isinstance(stream, BrokenPluginStream)
        with pytest.raises(Exception) as exc_info:
            len(stream)
        assert "Oops, broken plugin..." in str(exc_info)
