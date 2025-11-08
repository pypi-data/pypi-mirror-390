import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from olmoearth_run.shared.models.api.search_filters import DatetimeFilter, KeywordFilter, SortDirection
from olmoearth_run.shared.models.api.step import StepResponse
from olmoearth_run.shared.models.status import Status
from olmoearth_run.shared.models.task_results import WandbRunInfo
from olmoearth_run.shared.models.workflow_args import WorkflowArgs, WorkflowCreateArgs
from olmoearth_run.shared.models.workflow_notification_config import WorkflowNotificationConfig


class WorkflowMetrics(BaseModel):
    """
    This tracks some interesting metrics at the Workflow level.
    """
    request_area_sq_km: float | None = Field(default=None, description="The area of the request in square kilometers.")
    dataset_size_mb: float | None = Field(default=None, description="The size of the dataset in megabytes")
    total_compute_time_seconds: float | None = Field(default=None, description="The total compute time in seconds for this workflow")


class WorkflowResponse(BaseModel):
    """
    The model we provide when asked for a Workflow over the API
    """

    id: uuid.UUID
    args: WorkflowArgs
    external_id: str | None = Field(
        default=None,
        description="The provided external ID of the Workflow, if applicable.",
    )
    progress: int = Field(ge=0, le=100, description="The progress of the Workflow, from 0 to 100")
    status: Status = Field(description="The status of the Workflow")
    metrics: WorkflowMetrics = Field(description="Metrics related to the Workflow's execution")
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = Field(
        default=None,
        description="The date and time the Workflow was completed. Could be successful or failure",
    )
    error_message: str | None = Field(
        default=None,
        description="Error details if the Workflow failed",
    )
    notification_config: WorkflowNotificationConfig | None = Field(
        default=None,
        description="Notification configuration for this workflow, if any",
    )


class WorkflowResponseWithSteps(WorkflowResponse):
    """
    If we want to provide the full list of steps along with the workflow, use this model.
    """
    steps: list[StepResponse] = Field(
        description="The list of Steps that make up the Workflow",
    )


class WorkflowNotification(BaseModel):
    """Structure of the payload sent to clients when emitting Workflow status update notifications"""

    workflow: WorkflowResponseWithSteps = Field(description="The Workflow that triggered the notification")
    result_info: BaseModel | None = Field(description="If the workflow is complete, this contains the results")
    error_message: str | None = Field(
        default=None,
        description="Error details if the Workflow failed",
    )


class WorkflowCreateRequest(BaseModel):
    """
    The model we expect when creating a new Workflow.
    """
    args: WorkflowCreateArgs = Field(description="The arguments for the Workflow")
    external_id: str | None = Field(
        default=None,
        description="An optional external ID for the Workflow, useful for tracking in external systems.",
    )
    notification_config: WorkflowNotificationConfig | None = Field(
        default=None,
        description="Optional configuration for notifications related to this Workflow.",
    )


class WorkflowSortField(str, Enum):
    """Valid fields for sorting workflows in search results."""
    STATUS = "status"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    COMPLETED_AT = "completed_at"
    PROGRESS = "progress"


class FineTuningWorkflowResponse(BaseModel):
    """Response model for completed fine tuning workflows."""
    windows_count: int = Field(description="Number of labeled windows created during the fine-tuning workflow")
    model_pipeline_id: uuid.UUID = Field(description="The ID of the pipeline housing the newly fine-tuned model stage")
    wandb_run_info: WandbRunInfo = Field(description="Weights & Biases run information")


class SearchWorkflowsRequest(BaseModel):
    """Request model for searching workflows"""
    id: KeywordFilter[uuid.UUID] | None = None
    external_id: KeywordFilter[str] | None = None
    status: KeywordFilter[Status] | None = None
    created_at: DatetimeFilter | None = None
    updated_at: DatetimeFilter | None = None
    completed_at: DatetimeFilter | None = None

    # Pagination and sorting
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    sort_by: WorkflowSortField = Field(default=WorkflowSortField.CREATED_AT)
    sort_direction: SortDirection = Field(default=SortDirection.DESC)
