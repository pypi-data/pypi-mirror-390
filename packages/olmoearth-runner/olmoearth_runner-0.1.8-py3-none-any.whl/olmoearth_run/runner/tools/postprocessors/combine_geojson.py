from geojson_pydantic import Feature, FeatureCollection

from olmoearth_run.shared.models.prediction_geometry import PredictionRequestFeature, PredictionResultCollection, PredictionResultFeature
from olmoearth_run.runner.tools.postprocessors.postprocess_interface import PostprocessInterfaceVector


class CombineGeojson(PostprocessInterfaceVector):
    def process_window(self, window_request: PredictionRequestFeature, window_result: PredictionResultCollection) -> PredictionResultCollection:
        assert len(window_result.features) == 1
        output_feature = window_result.features[0]
        result: PredictionResultFeature = Feature(type="Feature", properties=output_feature.properties, geometry=window_request.geometry)
        return FeatureCollection(
            type="FeatureCollection",
            features=[result]
        )

    def process_partition(self, all_window_results: list[PredictionResultCollection]) -> PredictionResultCollection:
        return self._combine_features(all_window_results)

    def process_dataset(self, all_partitions_results: list[PredictionResultCollection]) -> PredictionResultCollection:
        return self._combine_features(all_partitions_results)

    def _combine_features(self, features: list[PredictionResultCollection]) -> PredictionResultCollection:
        combined_features: list[PredictionResultFeature] = []
        for partition_results in features:
            combined_features.extend(partition_results.features)
        return FeatureCollection(type="FeatureCollection", features=combined_features)
