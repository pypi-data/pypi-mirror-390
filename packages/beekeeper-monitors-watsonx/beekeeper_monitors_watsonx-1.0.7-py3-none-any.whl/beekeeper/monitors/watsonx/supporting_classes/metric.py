from typing import Dict, List, Literal, Optional

from pydantic.v1 import BaseModel


class WatsonxLocalMetric(BaseModel):
    """
    Provides the IBM watsonx.governance local monitor metric definition.

    Attributes:
        name (str): The name of the metric.
        data_type (str): The data type of the metric. Currently supports "string", "integer", "double", and "timestamp".
        nullable (bool, optional): Indicates whether the metric can be null. Defaults to `False`.

    Example:
        ```python
        from beekeeper.monitors.watsonx import WatsonxLocalMetric

        WatsonxLocalMetric(name="context_quality", data_type="double")
        ```
    """

    name: str
    data_type: Literal["string", "integer", "double", "timestamp"]
    nullable: bool = True

    def to_dict(self) -> Dict:
        return {"name": self.name, "type": self.data_type, "nullable": self.nullable}


class WatsonxMetricThreshold(BaseModel):
    """
    Defines the metric threshold for IBM watsonx.governance.

    Attributes:
        threshold_type (str): The threshold type. Can be either `lower_limit` or `upper_limit`.
        default_value (float): The metric threshold value.

    Example:
        ```python
        from beekeeper.monitors.watsonx import WatsonxMetricThreshold

        WatsonxMetricThreshold(threshold_type="lower_limit", default_value=0.8)
        ```
    """

    threshold_type: Literal["lower_limit", "upper_limit"]
    default_value: float = None

    def to_dict(self) -> Dict:
        return {"type": self.threshold_type, "default": self.default_value}


class WatsonxMetric(BaseModel):
    """
    Defines the IBM watsonx.governance global monitor metric.

    Attributes:
        name (str): The name of the metric.
        applies_to (List[str]): A list of task types that the metric applies to. Currently supports:
            "summarization", "generation", "question_answering", "extraction", and "retrieval_augmented_generation".
        thresholds (List[WatsonxMetricThreshold]): A list of metric thresholds associated with the metric.

    Example:
        ```python
        from beekeeper.monitors.watsonx import (
            WatsonxMetric,
            WatsonxMetricThreshold,
        )

        WatsonxMetric(
            name="context_quality",
            applies_to=["retrieval_augmented_generation", "summarization"],
            thresholds=[
                WatsonxMetricThreshold(threshold_type="lower_limit", default_value=0.75)
            ],
        )
        ```
    """

    name: str
    applies_to: List[
        Literal[
            "summarization",
            "generation",
            "question_answering",
            "extraction",
            "retrieval_augmented_generation",
        ]
    ]
    thresholds: Optional[List[WatsonxMetricThreshold]] = None

    def to_dict(self) -> Dict:
        from ibm_watson_openscale.base_classes.watson_open_scale_v2 import (
            ApplicabilitySelection,
            MetricThreshold,
        )

        monitor_metric = {
            "name": self.name,
            "applies_to": ApplicabilitySelection(problem_type=self.applies_to),
        }

        if self.thresholds is not None:
            monitor_metric["thresholds"] = [
                MetricThreshold(**threshold.to_dict()) for threshold in self.thresholds
            ]

        return monitor_metric
