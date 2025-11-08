"""
OlmoEarthRun configuration model representing the structure of olmoearth_run.yaml files.

This model captures the configuration structure for OlmoEarthRun workflows,
including partition strategies, postprocessing strategies, and window preparation.
"""

from typing import Any

import yaml  # type: ignore[import-untyped]
from pydantic import BaseModel, Field, field_validator

from olmoearth_run.shared.models.task_results import InferenceResultsDataType


class PartitionStrategiesConfig(BaseModel):
    """Configuration for partition strategies."""
    partition_request_geometry: dict[str, Any] = Field(
        description="Configuration for partitioning request geometry"
    )
    prepare_window_geometries: dict[str, Any] = Field(
        description="Configuration for preparing window geometries"
    )


class PostprocessingStrategiesConfig(BaseModel):
    """Configuration for postprocessing strategies."""
    process_window: dict[str, Any] = Field(
        description="Configuration for window-level postprocessing"
    )
    process_partition: dict[str, Any] = Field(
        description="Configuration for partition-level postprocessing"
    )
    process_dataset: dict[str, Any] = Field(
        description="Configuration for dataset-level postprocessing"
    )


class WindowPrepConfig(BaseModel):
    """Configuration for window preparation."""
    sampler: dict[str, Any] | None = Field(
        default=None,
        description="Configuration for sampler (optional, defaults to NoopSampler if not provided)"
    )
    labeled_window_preparer: dict[str, Any] = Field(
        description="Configuration for labeled window preparer"
    )
    data_splitter: dict[str, Any] = Field(
        description="Configuration for data splitter (mandatory)"
    )
    label_layer: str = Field(
        description="Name of the dataset layer where labeled windows should be written"
    )
    group_name: str = Field(
        default="default",
        description="Name of the group to store training windows",
    )
    split_property: str = Field(
        default="split",
        description="Name of the window options property to use for storing split assignment for training windows",
    )


class PredictionValue(BaseModel):
    """this is a single class value that the model can choose from on a given ClassificationField"""
    value: int | str = Field(description="The computer-friendly value stored in the raster or geojson")
    label: str = Field(description="The human-readable label for this value")
    color: tuple[int, int, int] | tuple[int, int, int, int] = Field(description="The RGB(A) color for this value")

    @field_validator("color", mode="after")
    @classmethod
    def validate_color_values(cls, v: tuple[int, int, int]) -> tuple[int, int, int]:
        """Validate that each RGB value is between 0 and 255."""
        for i, val in enumerate(v):
            if not 0 <= val <= 255:
                raise ValueError(f"Color value must be between 0 and 255, got {val}")
        return v


class ClassificationField(BaseModel):
    """A field the model will try to classify"""
    property_name: str = Field(
        description="The property field name in the geojson feature, or just the name of this band in a raster file"
    )
    confidence_property_name: str | None = Field(
        default=None,
        description="For vector results, if this field has a corresponding confidence field, the name of that field"
    )
    allowed_values: list[PredictionValue]
    band_index: int | None = Field(
        default=None,
        description="For raster results, the index of this field's band in the raster (1-based)"
    )
    confidence_band_index: int | None = Field(
        default=None,
        description="For raster results, if this field has a corresponding confidence value, the band of that field"
    )

    def build_colormap(self) -> dict[int, tuple[int, int, int, int]]:
        """Generates a rio_tiler compliant colormap and adds in alpha if missing"""
        return {
            int(av.value): av.color if len(av.color) == 4 else av.color + (255,)
            for av in self.allowed_values
        }


class RegressionField(BaseModel):
    """A field that the model tries to predict a continuous value of"""
    property_name: str = Field(
        description="The property field name in the geojson feature, or just the name of this band in a raster file")
    band_index: int | None = Field(
        default=None,
        description="For raster results, the index of this field's band in the raster (1-based)")
    min_value: float = Field(description="Minimum possible value for this field")
    max_value: float = Field(description="Maximum possible value for this field")
    colormap_name: str = Field(
        default="viridis",
        description="Name of the rio_tiler colormap to use, "
                    "see https://cogeotiff.github.io/rio-tiler/colormap/#default-rio-tilers-colormaps"
    )


class DetectionObject(BaseModel):
    """For detection models; this is an object the model is trying to detect"""
    detected_object_name: str = Field(description="The name of the object the model is trying to detect (e.g., 'car')")
    confidence_property_name: str | None = Field(
        default=None,
        description="For vector results, if there is a corresponding confidence field, this is the name of that field")
    confidence_band_index: int | None = Field(
        default=None,
        description="For raster results, if there is a corresponding confidence value, this the band of that field"
    )


class InferenceResultsConfig(BaseModel):
    """Configuration for inference results."""
    data_type: InferenceResultsDataType = Field(
        description="The type of predictions that this model returns. Options: RASTER, VECTOR"
    )
    classification_fields: list[ClassificationField] | None = Field(
        default=None,
        description="Classification legend mapping pixel values to labels and colors for raster outputs"
    )
    regression_fields: list[RegressionField] | None = Field(
        default=None,
        description='Fields that the model will predict a continous value on'
    )
    detection_objects: list[DetectionObject] | None = Field(
        default=None,
        description='For a detection model, this is the object(s) that the model is trying to find'
    )

    @field_validator("data_type", mode="before")
    @classmethod
    def uppercase_data_type(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.upper()
        return v


class OlmoEarthRunConfig(BaseModel):
    """
    Root configuration model for OlmoEarthRun YAML files.

    This model represents the structure of olmoearth_run.yaml configuration files
    used to configure OlmoEarthRun workflows. Each section contains dictionaries
    that will be used by OlmoEarthRunConfigLoader to instantiate the appropriate
    classes using the _instantiate_from_dict method.
    """

    inference_results_config: InferenceResultsConfig = Field(
        description="Configuration for inference results"
    )

    partition_strategies: PartitionStrategiesConfig = Field(
        description="Strategies for partitioning geometries"
    )
    postprocessing_strategies: PostprocessingStrategiesConfig = Field(
        description="Strategies for postprocessing results"
    )
    window_prep: WindowPrepConfig | None = Field(
        default=None,
        description="Configuration for window preparation including labeled window preparer and optional data splitter"
    )

    # Allow additional fields for other configuration that might exist
    # but isn't directly related to class loading
    model_config = {"extra": "allow"}

    @classmethod
    def from_yaml(cls, yaml_content: str) -> "OlmoEarthRunConfig":
        """
        Parse OlmoEarthRun configuration from a YAML string.

        Args:
            yaml_content: YAML content as a string

        Returns:
            OlmoEarthRunConfig object parsed from the YAML content

        Raises:
            ValueError: If the YAML content is malformed or doesn't match the expected structure
        """
        try:
            raw_config = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            raise ValueError("Invalid YAML in olmoearth_run_config") from e

        try:
            return cls.model_validate(raw_config)
        except Exception as e:  # Catch ValidationError and other pydantic errors
            raise ValueError(f"Invalid olmoearth_run_config structure. {e}") from e
