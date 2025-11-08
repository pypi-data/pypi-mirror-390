import os

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_USER = os.getenv("REDIS_USER")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_MAX_CONNECTIONS = int(os.getenv("REDIS_MAX_CONNECTIONS", "20"))

# The number of workers that should be employed to run tasks. Defaults to the number of CPUs available.
NUM_WORKERS = int(os.getenv("NUM_WORKERS", os.cpu_count() or 1))

# Task status database sync configuration
TASK_STATUS_SYNC_INTERVAL_SECONDS = int(os.getenv("TASK_STATUS_SYNC_INTERVAL_SECONDS", "300"))  # 5 minutes
TASK_STATUS_STALENESS_THRESHOLD_MINUTES = int(os.getenv("TASK_STATUS_STALENESS_THRESHOLD_MINUTES", "15"))
SYNC_JOB_REDIS_KEY = "olmoearth_run_sync_task_statuses_running"

# Bulk gcs transfer config
GCS_STORAGE_MANAGER_THREAD_COUNT = NUM_WORKERS*2
GCS_LS_PAGE_SIZE = int(os.getenv("GCS_LS_PAGE_SIZE", "5000"))

# The maximum degree of parallelism allowed when processing partitions. If a workflow creates more partitions
# than this number, multiple partitions will be assigned to a single task and processed serially.
MAX_PARTITION_PARALLELISM = int(os.getenv("MAX_PARTITION_PARALLELISM", "120"))

# The URL that executor workers should use to call the API
# This environment variable is required except for local runner.
OERUN_API_URL = os.environ.get("OERUN_API_URL", "")

# Weights and Biases (https://wandb.ai)
WANDB_API_KEY = os.getenv("WANDB_API_KEY", "")
WANDB_PROJECT = os.getenv("WANDB_PROJECT", "olmoearth_run_develop")
WANDB_ENTITY = os.getenv("WANDB_ENTITY", "eai-ai2")
WANDB_API_KEY_SECRET_PATH = os.getenv("WANDB_API_KEY_SECRET_PATH", "")

# PostgreSQL configuration
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB_NAME = os.getenv("POSTGRES_DB_NAME", "esrun")  # legacy name

GOOGLE_CLOUD_BUCKET_NAME = os.getenv("GOOGLE_CLOUD_BUCKET_NAME")
GOOGLE_CLOUD_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
GOOGLE_CLOUD_REGION = "us-west1"
GOOGLE_CLOUD_SERVICE_ACCOUNT_EMAIL = os.getenv("GOOGLE_CLOUD_SERVICE_ACCOUNT_EMAIL", "")
GOOGLE_CLOUD_TEMP_PREFIX = f"gs://{GOOGLE_CLOUD_BUCKET_NAME}/temp/"

OERUNNER_OTEL_COLLECTOR_BUCKET_NAME = os.getenv("OERUNNER_OTEL_COLLECTOR_BUCKET_NAME", "")
OERUNNER_OTEL_COLLECTOR_OBJECT_KEY = os.getenv("OERUNNER_OTEL_COLLECTOR_OBJECT_KEY", "")

# OTEL SDK configuration
OTEL_RESOURCE_ATTRIBUTES = os.getenv("OTEL_RESOURCE_ATTRIBUTES")  # e.g., "service.name=my-service"
OTEL_EXPORTER_OTLP_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
OTEL_METRIC_EXPORT_INTERVAL_MILLIS = int(os.getenv("OTEL_METRIC_EXPORT_INTERVAL_MILLIS", "10000"))  # 10 seconds

# The timeout in hours that we send to google batch.
MAX_TASK_RUN_DURATION_HOURS = float(os.getenv("MAX_TASK_RUN_DURATION_HOURS", "8"))
MAX_FINE_TUNING_TASK_DURATION_HOURS = float(os.getenv("MAX_FINE_TUNING_TASK_DURATION_HOURS", "120"))

# ElasticSearch configuration
ELASTIC_HOST = os.getenv("ELASTIC_HOST", "localhost")  # Used in local dev & CI.
ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")  # Can be empty in local dev & CI
ELASTIC_FEATURES_INDEX_NAME = os.getenv("ELASTIC_FEATURES_INDEX_NAME", "features")

# Admin UI configuration
ADMIN_UI_DIR = os.getenv("ADMIN_UI_DIR", "admin_ui/")
ADMIN_UI_PASSWORD = os.getenv("ADMIN_UI_PASSWORD")

# Task Metrics Dashboard configuration
TASK_METRICS_DASHBOARD_BASE_URL = os.getenv("TASK_METRICS_DASHBOARD_BASE_URL", "")

# Task Traces configuration
TASK_TRACE_BASE_URL = os.getenv("TASK_TRACE_BASE_URL", "https://console.cloud.google.com/traces/explorer")

# These are GCP secret paths. eg: projects/{project_id}/secrets/{SECRET_NAME}/versions/{version}
AWS_ACCESS_KEY_ID_SECRET_PATH = os.getenv("AWS_ACCESS_KEY_ID_SECRET_PATH", "")
AWS_ACCESS_KEY_SECRET_PATH = os.getenv("AWS_ACCESS_KEY_SECRET_PATH", "")
