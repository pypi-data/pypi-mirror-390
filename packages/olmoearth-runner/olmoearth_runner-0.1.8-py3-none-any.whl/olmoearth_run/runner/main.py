import argparse
import logging
import os
import signal
import sys
import uuid

from opentelemetry import trace
from opentelemetry.trace import SpanKind, StatusCode
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from olmoearth_run.api_clients.olmoearth_run.olmoearth_run_api_client import OlmoEarthRunApiClient
from olmoearth_run.config import OERUN_API_URL
from olmoearth_run.runner.metrics.gpu_utilization import instrument_gpus
from olmoearth_run.runner.steps.base_step_definition import BaseStepDefinition
from olmoearth_run.runner.steps.combine_partitions_step_definition import CombinePartitionsStepDefinition
from olmoearth_run.runner.steps.create_partitions_step_definition import CreatePartitionsStepDefinition
from olmoearth_run.runner.steps.dataset_build_from_windows_step_definition import DatasetBuildFromWindowsStepDefinition
from olmoearth_run.runner.steps.dataset_build_step_definition import DatasetBuildStepDefinition
from olmoearth_run.runner.steps.fine_tuning_step_definition import FineTuningStepDefinition
from olmoearth_run.runner.steps.postprocess_partition_step_definition import PostprocessPartitionStepDefinition
from olmoearth_run.runner.steps.prepare_labeled_windows_step_definition import PrepareLabeledWindowsStepDefinition
from olmoearth_run.runner.steps.run_inference_step_definition import RunInferenceStepDefinition
from olmoearth_run.shared.models.api.task import TaskResponseWithStepAndWorkflow
from olmoearth_run.shared.models.status import Status
from olmoearth_run.shared.models.step_type import StepType
from olmoearth_run.shared.telemetry.logging import configure_logging

# Configure logging at startup
configure_logging()
logger = logging.getLogger(__name__)


STEP_DEFS: dict[StepType, type[BaseStepDefinition]] = {
    StepType.CREATE_PARTITIONS: CreatePartitionsStepDefinition,
    StepType.DATASET_BUILD: DatasetBuildStepDefinition,
    StepType.DATASET_BUILD_FROM_WINDOWS: DatasetBuildFromWindowsStepDefinition,
    StepType.PREPARE_LABELED_WINDOWS: PrepareLabeledWindowsStepDefinition,
    StepType.FINE_TUNE: FineTuningStepDefinition,
    StepType.RUN_INFERENCE: RunInferenceStepDefinition,
    StepType.POSTPROCESS_PARTITION: PostprocessPartitionStepDefinition,
    StepType.COMBINE_PARTITIONS: CombinePartitionsStepDefinition
}


def main() -> None:
    """Main entry point for the oerunner command with OpenTelemetry."""
    # Initialize GPU metrics monitoring (cleanup happens automatically at exit via atexit)

    linked_span = os.environ.get("LINKED_SPAN")
    links = []
    if linked_span is not None and linked_span != "":
        parent_context = TraceContextTextMapPropagator().extract(carrier={
            "traceparent": linked_span,
        })
        parent_span_context = trace.get_current_span(parent_context).get_span_context()
        if parent_span_context.is_valid:
            links.append(trace.Link(parent_span_context))

    tracer = trace.get_tracer("olmoearth_run.runner.tracer")
    with tracer.start_as_current_span("olmoearth_run.runner.main", links=links, kind=SpanKind.SERVER) as span:
        instrument_gpus()
        try:
            _main()
            span.set_status(StatusCode.OK)
        except SystemExit as e:
            exit_code = e.code or 0
            if exit_code != 0:
                span.set_status(StatusCode.ERROR, f"Process exited with code {exit_code}")
            else:
                span.set_status(StatusCode.OK)
            sys.exit(exit_code)


def _main() -> None:
    """Main entry point for the oerunner command."""
    logger.info("Starting olmoearth runner")
    parser = argparse.ArgumentParser(description="OlmoEarthRun task runner")
    parser.add_argument("--task-id", type=uuid.UUID, required=True, help="Task ID to load and process")

    args = parser.parse_args()
    logger.info(f"Starting OlmoEarthRun task runner with args: {args}")
    task_id = args.task_id

    # Initialize OlmoEarthRun client
    client = OlmoEarthRunApiClient(base_url=OERUN_API_URL)

    # Let OlmoEarthRun know that we've started, and grab the full task
    task = _mark_task_running(task_id, client)

    # Install a sigterm handler in case we get killed
    def handle_sigterm(signum: int, frame: object) -> None:
        """Handle SIGTERM signal by marking the current task as failed."""
        logger.warning("Received SIGTERM signal")
        logger.info(f"Marking task {task_id} as FAILED due to SIGTERM")
        client.tasks.update_task(task_id, Status.FAILED)
        sys.exit(128 + signum)

    signal.signal(signal.SIGTERM, handle_sigterm)

    # Now try to execute the step
    step_def = None
    try:
        if not task.step:
            raise ValueError(f"Unexpected missing Step on {task.id=}")
        step_def = STEP_DEFS[task.step.step_type]()
        logger.info(f"Starting Running Step: {step_def.__class__.__name__}")
        results = step_def.run(task.args)
        logger.info(f"Step completed successfully: {step_def.__class__.__name__}")

        client.tasks.update_task(task.id, Status.COMPLETED, results)
    except Exception as e:
        logger.exception(f"Error executing task {task_id}: {e}")
        error_message = str(e)
        client.tasks.update_task(task_id, Status.FAILED, error_message=error_message)
        if step_def:
            step_def.on_task_error(task.args, e)
        raise


def _mark_task_running(task_id: uuid.UUID, client: OlmoEarthRunApiClient) -> TaskResponseWithStepAndWorkflow:
    try:
        task_response = client.tasks.update_task(task_id, Status.RUNNING)
        if not task_response.records:
            raise ValueError(f"Could not find: {task_id=} : {task_response}")

        task = task_response.records[0]
        if not task.workflow or not task.step:
            raise ValueError(f"Unexpected missing Workflow or Step for {task.id=}")
        logger.info(f"Loaded task: {task.id}, Step: {task.step.id}, Workflow: {task.workflow.id}")
        return task
    except Exception as e:
        raise Exception(f"Error loading {task_id=}: {e}") from e


if __name__ == "__main__":
    main()
