"""OpenTelemetry metrics helpers."""
import enum
from collections.abc import Callable, Iterable, Sequence

from opentelemetry.metrics import CallbackOptions, Counter, Histogram, Observation, ObservableGauge
from opentelemetry import metrics


METRICS_ROOT_NAMESPACE = "olmoearth_run"


class MetricsContext(enum.Enum):
    RUNNER = "runner"
    ORCHESTRATOR = "orchestrator"


class Metrics:
    def __init__(self, context: MetricsContext, namespace_suffix: str):
        self.context = context
        self.namespace_suffix = namespace_suffix
        self.meter = metrics.get_meter(self.namespace)

    @property
    def namespace(self) -> str:
        return f"{METRICS_ROOT_NAMESPACE}.{self.context.value}.{self.namespace_suffix}"

    def _mk_metric_name(self, name: str) -> str:
        return f"{self.namespace}.{name}"

    def create_counter(self, name: str, unit: str = "", description: str = "") -> Counter:
        full_name = self._mk_metric_name(name)
        return self.meter.create_counter(
            name=full_name,
            description=description,
            unit=unit,
        )

    def create_histogram(self, name: str, unit: str = "", description: str = "") -> Histogram:
        full_name = self._mk_metric_name(name)
        return self.meter.create_histogram(
            name=full_name,
            description=description,
            unit=unit,
        )

    def create_observable_gauge(self, name: str, callbacks: Sequence[Callable[[CallbackOptions], Iterable[Observation]]], unit: str = "", description: str = "") -> ObservableGauge:
        full_name = self._mk_metric_name(name)
        return self.meter.create_observable_gauge(
            name=full_name,
            description=description,
            unit=unit,
            callbacks=callbacks,
        )
