from olmoearth_run.shared.telemetry.metrics import Metrics, MetricsContext


metrics = Metrics(MetricsContext.RUNNER, "window_prep")


annotation_tasks_processed_counter = metrics.create_counter(
    name="annotation_tasks_processed",
    description="Number of annotation tasks processed",
    unit="1",
)

labeled_windows_prepared_counter = metrics.create_counter(
    name="labeled_windows_prepared",
    description="Number of windows prepared with labels",
    unit="1",
)
