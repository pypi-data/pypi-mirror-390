"""SDK for building singer-compliant Singer taps."""

from hotglue_tap_sdk import streams
from hotglue_tap_sdk.mapper_base import InlineMapper
from hotglue_tap_sdk.plugin_base import PluginBase
from hotglue_tap_sdk.sinks import BatchSink, RecordSink, Sink, SQLSink
from hotglue_tap_sdk.streams import (
    GraphQLStream,
    RESTStream,
    SQLConnector,
    SQLStream,
    Stream,
)
from hotglue_tap_sdk.tap_base import SQLTap, Tap
from hotglue_tap_sdk.target_base import SQLTarget, Target

__all__ = [
    "BatchSink",
    "GraphQLStream",
    "InlineMapper",
    "PluginBase",
    "RecordSink",
    "RESTStream",
    "Sink",
    "SQLConnector",
    "SQLSink",
    "SQLStream",
    "SQLTap",
    "SQLTarget",
    "Stream",
    "streams",
    "Tap",
    "Target",
]
