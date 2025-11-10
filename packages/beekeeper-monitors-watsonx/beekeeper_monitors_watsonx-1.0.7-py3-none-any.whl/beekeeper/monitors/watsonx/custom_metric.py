import datetime
import logging
import uuid
from typing import Any, Dict, List, Literal, Union

from beekeeper.monitors.watsonx.supporting_classes.credentials import (
    CloudPakforDataCredentials,
    IntegratedSystemCredentials,
)
from beekeeper.monitors.watsonx.supporting_classes.enums import Region
from beekeeper.monitors.watsonx.supporting_classes.metric import (
    WatsonxLocalMetric,
    WatsonxMetric,
)
from beekeeper.monitors.watsonx.utils.data_utils import validate_and_filter_dict
from beekeeper.monitors.watsonx.utils.instrumentation import suppress_output
from deprecated import deprecated


class WatsonxCustomMetricsManager:
    """
    Provides functionality to set up a custom metric to measure your model's performance with IBM watsonx.governance.

    Attributes:
        api_key (str): The API key for IBM watsonx.governance.
        region (Region, optional): The region where watsonx.governance is hosted when using IBM Cloud.
            Defaults to `us-south`.
        cpd_creds (CloudPakforDataCredentials, optional): IBM Cloud Pak for Data environment credentials.

    Example:
        ```python
        from beekeeper.monitors.watsonx import (
            WatsonxCustomMetricsManager,
            CloudPakforDataCredentials,
        )

        # watsonx.governance (IBM Cloud)
        wxgov_client = WatsonxCustomMetricsManager(api_key="API_KEY")

        # watsonx.governance (CP4D)
        cpd_creds = CloudPakforDataCredentials(
            url="CPD_URL",
            username="USERNAME",
            password="PASSWORD",
            version="5.0",
            instance_id="openshift",
        )

        wxgov_client = WatsonxCustomMetricsManager(cpd_creds=cpd_creds)
        ```
    """

    def __init__(
        self,
        api_key: str = None,
        region: Union[Region, str] = Region.US_SOUTH,
        cpd_creds: Union[CloudPakforDataCredentials, Dict] = None,
    ) -> None:
        from ibm_cloud_sdk_core.authenticators import IAMAuthenticator  # type: ignore
        from ibm_watson_openscale import APIClient as WosAPIClient  # type: ignore

        self.region = Region.from_value(region)
        self._api_key = api_key
        self._wos_client = None

        if cpd_creds:
            self._wos_cpd_creds = validate_and_filter_dict(
                cpd_creds.to_dict(),
                ["username", "password", "api_key", "disable_ssl_verification"],
                ["url"],
            )

        if not self._wos_client:
            try:
                if hasattr(self, "_wos_cpd_creds") and self._wos_cpd_creds:
                    from ibm_cloud_sdk_core.authenticators import (
                        CloudPakForDataAuthenticator,  # type: ignore
                    )

                    authenticator = CloudPakForDataAuthenticator(**self._wos_cpd_creds)

                    self._wos_client = WosAPIClient(
                        authenticator=authenticator,
                        service_url=self._wos_cpd_creds["url"],
                    )

                else:
                    from ibm_cloud_sdk_core.authenticators import (
                        IAMAuthenticator,  # type: ignore
                    )

                    authenticator = IAMAuthenticator(apikey=self._api_key)
                    self._wos_client = WosAPIClient(
                        authenticator=authenticator,
                        service_url=self.region.openscale,
                    )

            except Exception as e:
                logging.error(
                    f"Error connecting to IBM watsonx.governance (openscale): {e}",
                )
                raise

    def _add_integrated_system(
        self,
        credentials: IntegratedSystemCredentials,
        name: str,
        endpoint: str,
    ) -> str:
        custom_metrics_integrated_system = self._wos_client.integrated_systems.add(
            name=name,
            description="Integrated system created by Beekeeper.",
            type="custom_metrics_provider",
            credentials=credentials.to_dict(),
            connection={"display_name": name, "endpoint": endpoint},
        ).result

        return custom_metrics_integrated_system.metadata.id

    def _add_monitor_definitions(
        self,
        name: str,
        metrics: List[WatsonxMetric],
        schedule: bool,
    ):
        from ibm_watson_openscale.base_classes.watson_open_scale_v2 import (
            ApplicabilitySelection,
            MonitorInstanceSchedule,
            MonitorMetricRequest,
            MonitorRuntime,
            ScheduleStartTime,
        )

        _metrics = [MonitorMetricRequest(**metric.to_dict()) for metric in metrics]
        _monitor_runtime = None
        _monitor_schedule = None

        if schedule:
            _monitor_runtime = MonitorRuntime(type="custom_metrics_provider")
            _monitor_schedule = MonitorInstanceSchedule(
                repeat_interval=1,
                repeat_unit="hour",
                start_time=ScheduleStartTime(
                    type="relative",
                    delay_unit="minute",
                    delay=30,
                ),
            )

        custom_monitor_details = self._wos_client.monitor_definitions.add(
            name=name,
            metrics=_metrics,
            tags=[],
            schedule=_monitor_schedule,
            applies_to=ApplicabilitySelection(input_data_type=["unstructured_text"]),
            monitor_runtime=_monitor_runtime,
            background_mode=False,
        ).result

        return custom_monitor_details.metadata.id

    def _get_monitor_instance(self, subscription_id: str, monitor_definition_id: str):
        monitor_instances = self._wos_client.monitor_instances.list(
            monitor_definition_id=monitor_definition_id,
            target_target_id=subscription_id,
        ).result.monitor_instances

        if len(monitor_instances) == 1:
            return monitor_instances[0]
        else:
            return None

    def _update_monitor_instance(
        self,
        integrated_system_id: str,
        custom_monitor_id: str,
    ):
        payload = [
            {
                "op": "replace",
                "path": "/parameters",
                "value": {
                    "custom_metrics_provider_id": integrated_system_id,
                    "custom_metrics_wait_time": 60,
                    "enable_custom_metric_runs": True,
                },
            },
        ]

        return self._wos_client.monitor_instances.update(
            custom_monitor_id,
            payload,
            update_metadata_only=True,
        ).result

    def _get_patch_request_field(
        self,
        field_path: str,
        field_value: Any,
        op_name: str = "replace",
    ) -> Dict:
        return {"op": op_name, "path": field_path, "value": field_value}

    def _get_dataset_id(
        self,
        subscription_id: str,
        data_set_type: Literal["feedback", "payload_logging"],
    ) -> str:
        data_sets = self._wos_client.data_sets.list(
            target_target_id=subscription_id,
            type=data_set_type,
        ).result.data_sets
        data_set_id = None
        if len(data_sets) > 0:
            data_set_id = data_sets[0].metadata.id
        return data_set_id

    def _get_dataset_data(self, data_set_id: str):
        json_data = self._wos_client.data_sets.get_list_of_records(
            data_set_id=data_set_id,
            format="list",
        ).result

        if not json_data.get("records"):
            return None

        return json_data["records"][0]

    def _get_existing_data_mart(self):
        data_marts = self._wos_client.data_marts.list().result.data_marts
        if len(data_marts) == 0:
            raise Exception(
                "No data marts found. Please ensure at least one data mart is available.",
            )

        return data_marts[0].metadata.id

    # ===== Global Custom Metrics =====
    @deprecated(
        reason="'add_metric_definition()' is deprecated and will be removed in a future version. Use 'create_metric_definition()' instead.",
        version="1.0.6",
        action="always",
    )
    def add_metric_definition(
        self,
        name: str,
        metrics: List[WatsonxMetric],
        integrated_system_url: str,
        integrated_system_credentials: IntegratedSystemCredentials,
        schedule: bool = False,
    ):
        return self.create_metric_definition(
            name=name,
            metrics=metrics,
            integrated_system_url=integrated_system_url,
            integrated_system_credentials=integrated_system_credentials,
            schedule=schedule,
        )

    def create_metric_definition(
        self,
        name: str,
        metrics: List[WatsonxMetric],
        integrated_system_url: str,
        integrated_system_credentials: IntegratedSystemCredentials,
        schedule: bool = False,
    ):
        """
        Creates a custom metric definition for IBM watsonx.governance.

        This must be done before using custom metrics.

        Args:
            name (str): The name of the custom metric group.
            metrics (List[WatsonxMetric]): A list of metrics to be measured.
            schedule (bool, optional): Enable or disable the scheduler. Defaults to `False`.
            integrated_system_url (str): The URL of the external metric provider.
            integrated_system_credentials (IntegratedSystemCredentials): The credentials for the integrated system.

        Example:
            ```python
            from beekeeper.monitors.watsonx import (
                WatsonxMetric,
                IntegratedSystemCredentials,
                WatsonxMetricThreshold,
            )

            wxgov_client.create_metric_definition(
                name="Custom Metric - Custom LLM Quality",
                metrics=[
                    WatsonxMetric(
                        name="context_quality",
                        applies_to=[
                            "retrieval_augmented_generation",
                            "summarization",
                        ],
                        thresholds=[
                            WatsonxMetricThreshold(
                                threshold_type="lower_limit", default_value=0.75
                            )
                        ],
                    )
                ],
                integrated_system_url="IS_URL",  # URL to the endpoint computing the metric
                integrated_system_credentials=IntegratedSystemCredentials(
                    auth_type="basic", username="USERNAME", password="PASSWORD"
                ),
            )
            ```
        """
        integrated_system_id = self._add_integrated_system(
            integrated_system_credentials,
            name,
            integrated_system_url,
        )

        external_monitor_id = suppress_output(
            self._add_monitor_definitions,
            name,
            metrics,
            schedule,
        )

        # Associate the external monitor with the integrated system
        payload = [
            {
                "op": "add",
                "path": "/parameters",
                "value": {"monitor_definition_ids": [external_monitor_id]},
            },
        ]

        self._wos_client.integrated_systems.update(integrated_system_id, payload)

        return {
            "integrated_system_id": integrated_system_id,
            "monitor_definition_id": external_monitor_id,
        }

    @deprecated(
        reason="'add_observer_instance()' is deprecated and will be removed in a future version. Use 'attach_monitor_instance()' from 'beekeeper-monitors-watsonx' instead.",
        version="1.0.5",
        action="always",
    )
    def add_observer_instance(
        self,
        integrated_system_id: str,
        monitor_definition_id: str,
        subscription_id: str,
    ):
        return self.attach_monitor_instance(
            integrated_system_id=integrated_system_id,
            monitor_definition_id=monitor_definition_id,
            subscription_id=subscription_id,
        )

    @deprecated(
        reason="'add_monitor_instance()' is deprecated and will be removed in a future version. Use 'attach_monitor_instance()' from 'beekeeper-monitors-watsonx' instead.",
        version="1.0.6",
        action="always",
    )
    def add_monitor_instance(
        self,
        integrated_system_id: str,
        monitor_definition_id: str,
        subscription_id: str,
    ):
        return self.attach_monitor_instance(
            integrated_system_id=integrated_system_id,
            monitor_definition_id=monitor_definition_id,
            subscription_id=subscription_id,
        )

    def attach_monitor_instance(
        self,
        integrated_system_id: str,
        monitor_definition_id: str,
        subscription_id: str,
    ):
        """
        Attaches the specified monitor definition to the specified subscription.

        Args:
            integrated_system_id (str): The ID of the integrated system.
            monitor_definition_id (str): The ID of the custom metric monitor instance.
            subscription_id (str): The ID of the subscription to associate the monitor with.

        Example:
            ```python
            wxgov_client.attach_monitor_instance(
                integrated_system_id="019667ca-5687-7838-8d29-4ff70c2b36b0",
                monitor_definition_id="custom_llm_quality",
                subscription_id="0195e95d-03a4-7000-b954-b607db10fe9e",
            )
            ```
        """
        from ibm_watson_openscale.base_classes.watson_open_scale_v2 import Target

        data_marts = self._wos_client.data_marts.list().result.data_marts
        if len(data_marts) == 0:
            raise Exception(
                "No data marts found. Please ensure at least one data mart is available.",
            )

        data_mart_id = data_marts[0].metadata.id
        existing_monitor_instance = self._get_monitor_instance(
            subscription_id,
            monitor_definition_id,
        )

        if existing_monitor_instance is None:
            target = Target(target_type="subscription", target_id=subscription_id)

            parameters = {
                "custom_metrics_provider_id": integrated_system_id,
                "custom_metrics_wait_time": 60,
                "enable_custom_metric_runs": True,
            }

            monitor_instance_details = suppress_output(
                self._wos_client.monitor_instances.create,
                data_mart_id=data_mart_id,
                background_mode=False,
                monitor_definition_id=monitor_definition_id,
                target=target,
                parameters=parameters,
            ).result
        else:
            existing_instance_id = existing_monitor_instance.metadata.id
            monitor_instance_details = self._update_monitor_instance(
                integrated_system_id,
                existing_instance_id,
            )

        return monitor_instance_details

    def publish_metrics(
        self,
        monitor_instance_id: str,
        run_id: str,
        request_records: Dict[str, Union[float, int]],
    ):
        """
        Publishes computed metrics to the specified global monitor instance.

        Args:
            monitor_instance_id (str): The unique ID of the monitor instance.
            run_id (str): The ID of the monitor run that generated the metrics.
            request_records (Dict[str | float | int]): Dict containing the metrics to be published.

        Example:
            ```python
            wxgov_client.publish_metrics(
                monitor_instance_id="01966801-f9ee-7248-a706-41de00a8a998",
                run_id="RUN_ID",
                request_records={"context_quality": 0.914, "sensitivity": 0.85},
            )
            ```
        """
        from ibm_watson_openscale.base_classes.watson_open_scale_v2 import (
            MonitorMeasurementRequest,
            Runs,
        )

        measurement_request = MonitorMeasurementRequest(
            timestamp=datetime.datetime.now(datetime.timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ",
            ),
            run_id=run_id,
            metrics=[request_records],
        )

        self._wos_client.monitor_instances.add_measurements(
            monitor_instance_id=monitor_instance_id,
            monitor_measurement_request=[measurement_request],
        ).result

        run = Runs(watson_open_scale=self._wos_client)
        patch_payload = []
        patch_payload.append(self._get_patch_request_field("/status/state", "finished"))
        patch_payload.append(
            self._get_patch_request_field(
                "/status/completed_at",
                datetime.datetime.now(datetime.timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%S.%fZ",
                ),
            ),
        )

        return run.update(
            monitor_instance_id=monitor_instance_id,
            monitoring_run_id=run_id,
            json_patch_operation=patch_payload,
        ).result

    # ===== Local Custom Metrics =====
    @deprecated(
        reason="'add_local_metric_definition()' is deprecated and will be removed in a future version. Use 'create_local_metric_definition()' from 'beekeeper-monitors-watsonx' instead.",
        version="1.0.6",
        action="always",
    )
    def add_local_metric_definition(
        self,
        name: str,
        metrics: List[WatsonxMetric],
        subscription_id: str,
    ):
        return self.create_local_metric_definition(
            name=name,
            metrics=metrics,
            subscription_id=subscription_id,
        )

    def create_local_metric_definition(
        self,
        name: str,
        metrics: List[WatsonxLocalMetric],
        subscription_id: str,
    ) -> str:
        """
        Creates a custom metric definition to compute metrics at the local (transaction) level for IBM watsonx.governance.

        Args:
            name (str): The name of the custom transaction metric group.
            metrics (List[WatsonxLocalMetric]): A list of metrics to be monitored at the local (transaction) level.
            subscription_id (str): The IBM watsonx.governance subscription ID associated with the metric definition.

        Example:
            ```python
            from beekeeper.monitors.watsonx import WatsonxLocalMetric

            wxgov_client.create_local_metric_definition(
                name="Custom LLM Local Metric",
                subscription_id="019674ca-0c38-745f-8e9b-58546e95174e",
                metrics=[
                    WatsonxLocalMetric(name="context_quality", data_type="double")
                ],
            )
            ```
        """
        from ibm_watson_openscale.base_classes.watson_open_scale_v2 import (
            LocationTableName,
            SparkStruct,
            SparkStructFieldPrimitive,
            Target,
        )

        target = Target(target_id=subscription_id, target_type="subscription")
        data_mart_id = self._get_existing_data_mart()
        metrics = [SparkStructFieldPrimitive(**metric.to_dict()) for metric in metrics]

        schema_fields = [
            SparkStructFieldPrimitive(
                name="scoring_id",
                type="string",
                nullable=False,
            ),
            SparkStructFieldPrimitive(
                name="run_id",
                type="string",
                nullable=True,
            ),
            SparkStructFieldPrimitive(
                name="computed_on",
                type="string",
                nullable=False,
            ),
        ]

        schema_fields.extend(metrics)

        data_schema = SparkStruct(type="struct", fields=schema_fields)

        return self._wos_client.data_sets.add(
            target=target,
            name=name,
            type="custom",
            data_schema=data_schema,
            data_mart_id=data_mart_id,
            location=LocationTableName(
                table_name=name.lower().replace(" ", "_") + "_" + str(uuid.uuid4())[:8],
            ),
            background_mode=False,
        ).result.metadata.id

    def publish_local_metrics(
        self,
        metric_instance_id: str,
        request_records: List[Dict],
    ):
        """
        Publishes computed metrics to the specified transaction record.

        Args:
            metric_instance_id (str): The unique ID of the custom transaction metric.
            request_records (List[Dict]): A list of dictionaries containing the records to be stored.

        Example:
            ```python
            wxgov_client.publish_local_metrics(
                metric_instance_id="0196ad39-1b75-7e77-bddb-cc5393d575c2",
                request_records=[
                    {
                        "scoring_id": "304a9270-44a1-4c4d-bfd4-f756541011f8",
                        "run_id": "RUN_ID",
                        "computed_on": "payload",
                        "context_quality": 0.786,
                    }
                ],
            )
            ```
        """
        return self._wos_client.data_sets.store_records(
            data_set_id=metric_instance_id,
            request_body=request_records,
        ).result

    def list_local_metrics(
        self,
        metric_instance_id: str,
    ):
        """
        Lists records from a custom local metric definition.

        Args:
            metric_instance_id (str): The unique ID of the custom transaction metric.

        Example:
            ```python
            wxgov_client.list_local_metrics(
                metric_instance_id="0196ad47-c505-73c0-9d7b-91c082b697e3"
            )
            ```
        """
        return self._get_dataset_data(metric_instance_id)


@deprecated(
    reason="'WatsonxCustomMetric()' is deprecated and will be removed in a future version. "
    "Use 'WatsonxCustomMetricsManager' instead.",
    version="1.0.6",
    action="always",
)
class WatsonxCustomMetric(WatsonxCustomMetricsManager):
    pass
