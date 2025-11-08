import uuid
from typing import Annotated, Literal, TypeVar

from pydantic import BaseModel, Field

from olmoearth_run.shared.models.prediction_geometry import PredictionRequestCollection
from olmoearth_run.shared.models.workflow_type import WorkflowType
from olmoearth_run.shared.tools.gcs_tools import read_text_from_gcs


class BaseWorkflowArgs(BaseModel):
    workflow_type: WorkflowType = Field(
        description="The enumerated string identifying the category of Workflow being represented"
    )


class PredictionWorkflowCreateArgs(BaseWorkflowArgs):
    """Set of arguments required for creating a Prediction Workflow"""

    workflow_type: Literal[WorkflowType.PREDICTION] = Field(default=WorkflowType.PREDICTION)
    model_pipeline_id: uuid.UUID = Field(
        description="The ID of the ModelPipeline to be run for this prediction Workflow"
    )
    geometry: PredictionRequestCollection = Field(description="A GeoJSON feature collection specifying geometries and time ranges on which to run prediction")


class PredictionWorkflowArgs(BaseWorkflowArgs):
    workflow_type: Literal[WorkflowType.PREDICTION] = Field(default=WorkflowType.PREDICTION)
    model_pipeline_id: uuid.UUID = Field(
        description="The ID of the ModelPipeline to be run for this prediction Workflow"
    )
    geometry_gcs_path: str = Field(description="GCS path to the GeoJSON file specifying geometries and time ranges on which to run prediction")
    min_window_success_rate: float | None = Field(default=0.9, description="Minimum required ratio of non-rejected windows (prepared + skipped) to total windows. If None, the check is skipped.")

    def load_geometry(self) -> PredictionRequestCollection:
        """Load and return the PredictionRequestCollection from GCS."""
        geojson = read_text_from_gcs(self.geometry_gcs_path)
        return PredictionRequestCollection.model_validate_json(geojson)


class DatasetBuildFromWindowsWorkflowArgs(BaseWorkflowArgs):
    """Arguments for building a dataset from pre-created windows."""
    workflow_type: Literal[WorkflowType.DATASET_BUILD_FROM_WINDOWS] = Field(default=WorkflowType.DATASET_BUILD_FROM_WINDOWS)
    container_image_id: uuid.UUID = Field(description="The ID of the container image to build the dataset with")
    dataset_path: str = Field(description="Path to the dataset with pre-created windows")
    total_workers: int = Field(default=1, description="Number of parallel tasks to create for processing windows")
    min_window_success_rate: float | None = Field(default=0.9, description="Minimum required ratio of non-rejected windows (prepared + skipped) to total windows. If None, the check is skipped.")


class FineTuningWorkflowArgs(BaseWorkflowArgs):
    """Set of arguments required for running a Fine Tuning Workflow"""

    workflow_type: Literal[WorkflowType.FINE_TUNING] = Field(default=WorkflowType.FINE_TUNING)
    annotation_features_path: str = Field(description="Path to the GeoJSON file containing annotation features")
    annotation_task_features_path: str = Field(description="Path to the GeoJSON file containing annotation task features")
    foundation_model_id: uuid.UUID = Field(description="The ID of foundation model to be staged for fine-tuning")
    container_image_id: uuid.UUID = Field(description="The ID of the container image to be used for fine-tuning")
    olmoearth_run_config_yaml: str = Field(description="The OlmoEarthRun configuration (YAML string)")
    dataset_config_json: str = Field(description="The dataset config that will be used to build the dataset (JSON string)")
    model_config_yaml: str = Field(description="The model config that will be used to train the model (YAML string)")
    model_name_prefix: str = Field(description="Prefix for the resulting fine-tuned model pipeline name (timestamp will be appended)")
    min_window_success_rate: float | None = Field(default=0.9, description="Minimum required ratio of non-rejected windows (prepared + skipped) to total windows. If None, the check is skipped.")


WorkflowArgs = Annotated[
    FineTuningWorkflowArgs | PredictionWorkflowArgs | DatasetBuildFromWindowsWorkflowArgs,
    Field(discriminator='workflow_type')
]
WorkflowArgsType = TypeVar("WorkflowArgsType", bound=WorkflowArgs)

# The arguments used to create a workflow (may differ from stored args)
WorkflowCreateArgs = Annotated[
    FineTuningWorkflowArgs | PredictionWorkflowCreateArgs | DatasetBuildFromWindowsWorkflowArgs,
    Field(discriminator='workflow_type')
]
WorkflowCreateArgsType = TypeVar("WorkflowCreateArgsType", bound=WorkflowCreateArgs)
