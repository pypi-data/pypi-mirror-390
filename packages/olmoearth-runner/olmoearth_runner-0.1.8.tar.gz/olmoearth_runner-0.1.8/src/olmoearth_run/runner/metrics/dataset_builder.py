from olmoearth_run.shared.telemetry.metrics import Metrics, MetricsContext


metrics = Metrics(MetricsContext.RUNNER, "dataset_builder")

LOADING_PREFIX = "loading"
PREPARE_PREFIX = "prepare"
INGEST_PREFIX = "ingest"
MATERIALIZEX_PREFIX = "materialize"


# LOADING
load_windows_loaded_counter = metrics.create_counter(
    name=f"{LOADING_PREFIX}.windows_loaded",
    description="Number of windows loaded",
    unit="1",
)


# PREPARE
prepare_windows_processed_counter = metrics.create_counter(
    name=f"{PREPARE_PREFIX}.windows_processed",
    description="Number of windows processed for preparation",
    unit="1",
)
prepare_window_layers_handled_counter = metrics.create_counter(
    name=f"{PREPARE_PREFIX}.layers.windows_handled",
    description="Number of window layers handled per data source, with skipped status",
    unit="1",
)
prepare_window_layers_handle_attempts_counter = metrics.create_counter(
    name=f"{PREPARE_PREFIX}.layers.windows_handle_attempts",
    description="Number of attempts to handle window layers per data source",
    unit="1",
)
prepare_window_rejection_ratio_error_counter = metrics.create_counter(
    name=f"{PREPARE_PREFIX}.rejection_ratio_error",
    description="Number of times window success rate fell below threshold",
    unit="1",
)


# INGEST
ingest_jobs_processed_counter = metrics.create_counter(
    name=f"{INGEST_PREFIX}.jobs_processed",
    description="Number of jobs processed for ingestion",
    unit="1",
)
ingest_geometries_ingested_counter = metrics.create_counter(
    name=f"{INGEST_PREFIX}.geometries_ingested",
    description="Number of geometries ingested, by data source, with outcome",
    unit="1",
)


# MATERIALIZE
materialize_windows_processed_counter = metrics.create_counter(
    name=f"{MATERIALIZEX_PREFIX}.windows_processed",
    description="Number of windows processed for materialization",
    unit="1",
)
materialize_window_layers_materialized_counter = metrics.create_counter(
    name=f"{MATERIALIZEX_PREFIX}.layers.windows_materialized",
    description="Number of window layers materialized, by data source",
    unit="1",
)
materialize_window_layers_materialize_attempts_counter = metrics.create_counter(
    name=f"{MATERIALIZEX_PREFIX}.layers.windows_materialize_attempts",
    description="Number of attempts to materialize window layers, by data source",
    unit="1",
)
