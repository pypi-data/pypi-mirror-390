"""
GPU Utilization Monitoring with OpenTelemetry Observable Gauges.

This module uses pynvml to collect GPU utilization metrics and exposes them
via OpenTelemetry Observable Gauges, which are sampled automatically by the
OTEL SDK at collection time.
"""

import atexit
import logging
from collections.abc import Iterable
from dataclasses import dataclass

from opentelemetry.metrics import CallbackOptions, Observation
from pynvml import (  # type: ignore[import-untyped]
    nvmlDeviceGetCount,
    nvmlDeviceGetHandleByIndex,
    nvmlDeviceGetMemoryInfo,
    nvmlDeviceGetName,
    nvmlDeviceGetUtilizationRates,
    NVMLError,
    nvmlInit,
    nvmlShutdown,
)

from olmoearth_run.shared.telemetry.metrics import Metrics, MetricsContext


logger = logging.getLogger(__name__)
metrics = Metrics(MetricsContext.RUNNER, "gpu_utilization")


@dataclass
class GPUUtilization:
    """GPU utilization metrics for a single device."""
    device_index: int
    device_name: str
    gpu_percent: float  # GPU processor utilization percentage
    memory_percent: float  # GPU memory utilization percentage


def get_device_utilizations() -> list[GPUUtilization] | None:
    """
    Get current GPU utilization metrics for all devices.

    Returns:
        List of GPUUtilization objects, one per device, or None if unavailable.
    """
    try:
        utils = []

        for device_index in range(nvmlDeviceGetCount()):
            device_handle = nvmlDeviceGetHandleByIndex(device_index)
            util = nvmlDeviceGetUtilizationRates(device_handle)
            mem_info = nvmlDeviceGetMemoryInfo(device_handle)
            device_name = nvmlDeviceGetName(device_handle)

            utils.append(
                GPUUtilization(
                    device_index=device_index,
                    device_name=device_name if isinstance(device_name, str) else device_name.decode('utf-8'),
                    gpu_percent=float(util.gpu),
                    memory_percent=float(mem_info.used) / float(mem_info.total) * 100.0,
                )
            )

        return utils

    except NVMLError as e:
        # Don't crash if GPU metrics are unavailable
        logger.warning(f"Could not get GPU device info: {e}")
        return None


def _gpu_processor_utilization_callback(options: CallbackOptions) -> Iterable[Observation]:
    """
    Callback for GPU processor utilization observable gauge.

    Called automatically by the OTEL SDK at collection time.
    Yields one observation per GPU device.
    """
    utilizations = get_device_utilizations()

    if utilizations:
        for util in utilizations:
            attributes = {
                "gpu_number": str(util.device_index),
                "gpu_name": util.device_name,
            }
            yield Observation(util.gpu_percent, attributes=attributes)


def _gpu_memory_utilization_callback(options: CallbackOptions) -> Iterable[Observation]:
    """
    Callback for GPU memory utilization observable gauge.

    Called automatically by the OTEL SDK at collection time.
    Yields one observation per GPU device.
    """
    utilizations = get_device_utilizations()

    if utilizations:
        for util in utilizations:
            attributes = {
                "gpu_number": str(util.device_index),
                "gpu_name": util.device_name,
            }
            yield Observation(util.memory_percent, attributes=attributes)


def _cleanup_nvml() -> None:
    """Cleanup function to shut down NVML at program exit."""
    try:
        logger.info("Shutting down NVML")
        nvmlShutdown()
    except Exception as e:
        logger.warning(f"Error during NVML shutdown: {e}")


def instrument_gpus() -> None:
    """
    Initialize GPU utilization monitoring with OpenTelemetry.

    Initializes NVML and registers GPU utilization observable gauges.
    NVML cleanup is automatically registered to run at program exit via atexit.

    The OTEL SDK will automatically call the registered callbacks at
    collection time (controlled by the MetricReader configuration).

    If GPU initialization fails (e.g., no GPUs available), logs a message
    and continues without GPU metrics.
    """
    try:
        # Initialize NVML
        logger.info("Initializing NVML for GPU monitoring")
        nvmlInit()

        # Register cleanup to run at exit
        atexit.register(_cleanup_nvml)

        # Create observable gauge for GPU processor utilization
        metrics.create_observable_gauge(
            name="processor",
            callbacks=[_gpu_processor_utilization_callback],
            unit="%",
        )

        # Create observable gauge for GPU memory utilization
        metrics.create_observable_gauge(
            name="memory",
            callbacks=[_gpu_memory_utilization_callback],
            unit="%",
        )

        logger.info("GPU utilization metrics initialized successfully")

    except Exception as e:
        logger.info(f"Could not initialize GPU metrics. No GPUs available or encountered error: {e}")
