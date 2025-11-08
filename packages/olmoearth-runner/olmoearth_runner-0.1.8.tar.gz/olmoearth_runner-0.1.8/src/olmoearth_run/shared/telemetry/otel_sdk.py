"""OpenTelemetry SDK initialization utilities."""
import os

from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.metrics import Histogram
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.metrics.view import View
from opentelemetry.sdk.metrics._internal.aggregation import ExponentialBucketHistogramAggregation
from opentelemetry.sdk.resources import Resource

from olmoearth_run.config import (
    OTEL_EXPORTER_OTLP_ENDPOINT,
    OTEL_METRIC_EXPORT_INTERVAL_MILLIS,
    OTEL_RESOURCE_ATTRIBUTES,
)


def initialize_otel() -> None:
    """
    Initialize OpenTelemetry SDK for observability.

    OTEL SDK needs to be initialized in each process that emits telemetry for correctness.
    This function abstracts the complexity of initializing the SDK and setting the global provider.

    OTEL SDK can be configured to emit:

    1. Metrics, via a MeterProvider with an OTLP exporter (we initialize this below)
    2. Traces, via a TracerProvider with an OTLP exporter (we deliberately opt out at this time)
    3. Logs, via a LoggerProvider with an OTLP exporter (we deliberately opt out at this time)

    This function takes no explicit args, but reads configuration from config.py
    (which in turn reads from environment variables):

        OTEL_RESOURCE_ATTRIBUTES: Should include service.name=<name>
            Example: "service.name=olmoearth-run-orchestrator-api"

        OTEL_EXPORTER_OTLP_ENDPOINT: OTLP endpoint (default: http://localhost:4317)

        OTEL_METRIC_EXPORT_INTERVAL_MILLIS: Export interval in ms (default: 10000)

    Note:
        worker_pid is automatically set to the current process ID to ensure
        metrics from different workers/processes have unique identities.
        This prevents "Duplicate TimeSeries" errors in multi-worker setups.
    """
    # Parse OTEL_RESOURCE_ATTRIBUTES (from config.py)
    # Format: "key1=value1,key2=value2"
    base_attributes = {}
    if OTEL_RESOURCE_ATTRIBUTES:
        for pair in OTEL_RESOURCE_ATTRIBUTES.split(","):
            if "=" in pair:
                key, value = pair.split("=", 1)
                base_attributes[key.strip()] = value.strip()

    # Build resource attributes
    resource_attributes = {
        "service.name": base_attributes.get("service.name", "unknown"),  # Fallback for local dev
        "worker_pid": str(os.getpid()),  # Unique worker identifier (prevents duplicate time series)
        **base_attributes,  # Include any additional attributes from env
    }

    resource = Resource.create(resource_attributes)

    # Create OTLP metric exporter.
    # Should point at an endpoint implementing the OTLP protocol,
    # such as an OTEL collector sidecar or local process.
    metric_exporter = OTLPMetricExporter(endpoint=OTEL_EXPORTER_OTLP_ENDPOINT)

    # Create metric reader with periodic export
    metric_reader = PeriodicExportingMetricReader(
        exporter=metric_exporter,
        export_interval_millis=OTEL_METRIC_EXPORT_INTERVAL_MILLIS,
    )

    # Configure all histograms to use exponential bucketing
    # Exponential histograms automatically adjust bucket boundaries based on data distribution,
    # providing better accuracy without needing to pre-specify bucket bounds.
    # This is especially useful for latency metrics which can vary widely.
    histogram_view = View(
        instrument_type=Histogram,  # Apply only to Histogram instruments
        aggregation=ExponentialBucketHistogramAggregation(),
    )

    # Create and set global MeterProvider
    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=[metric_reader],
        views=[histogram_view],  # Apply exponential histogram to all histogram instruments
    )
    metrics.set_meter_provider(meter_provider)

    # Maybe one day: tracing
    # Probably soon, for runner only: logging
