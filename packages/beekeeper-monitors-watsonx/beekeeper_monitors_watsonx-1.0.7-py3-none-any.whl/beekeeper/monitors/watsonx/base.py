import json
import logging
import os
import uuid
from typing import Dict, List, Literal, Union

import certifi
from beekeeper.core.monitors import PromptMonitor
from beekeeper.core.monitors.types import PayloadRecord
from beekeeper.core.prompts.utils import extract_template_vars
from beekeeper.monitors.watsonx.supporting_classes.credentials import (
    CloudPakforDataCredentials,
)
from beekeeper.monitors.watsonx.supporting_classes.enums import Region
from beekeeper.monitors.watsonx.utils.data_utils import validate_and_filter_dict
from beekeeper.monitors.watsonx.utils.instrumentation import suppress_output
from deprecated import deprecated

os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
logging.getLogger("ibm_watsonx_ai.client").setLevel(logging.ERROR)
logging.getLogger("ibm_watsonx_ai.wml_resource").setLevel(logging.ERROR)


def _convert_payload_format(
    records: List[Dict],
    feature_fields: List[str],
) -> List[Dict]:
    payload_data = []
    response_fields = ["generated_text", "input_token_count", "generated_token_count"]

    for record in records:
        request = {"parameters": {"template_variables": {}}}
        results = {}

        request["parameters"]["template_variables"] = {
            field: str(record.get(field, "")) for field in feature_fields
        }

        results = {
            field: record.get(field) for field in response_fields if record.get(field)
        }

        pl_record = {
            "request": request,
            "response": {"results": [results]},
            "scoring_id": str(uuid.uuid4()),
        }

        if "response_time" in record:
            pl_record["response_time"] = record["response_time"]

        payload_data.append(pl_record)

    return payload_data


class WatsonxExternalPromptMonitor(PromptMonitor):
    """
    Provides functionality to interact with IBM watsonx.governance for monitoring prompts executed on external LLMs.

    Note:
        One of the following parameters is required to create a prompt monitor:
        `project_id` or `space_id`, but not both.

    Attributes:
        api_key (str): The API key for IBM watsonx.governance.
        space_id (str, optional): The space ID in watsonx.governance.
        project_id (str, optional): The project ID in watsonx.governance.
        region (Region, optional): The region where watsonx.governance is hosted when using IBM Cloud.
            Defaults to `us-south`.
        cpd_creds (CloudPakforDataCredentials, optional): The Cloud Pak for Data environment credentials.
        subscription_id (str, optional): The subscription ID associated with the records being logged.

    Example:
        ```python
        from beekeeper.monitors.watsonx import (
            WatsonxExternalPromptMonitor,
            CloudPakforDataCredentials,
        )

        # watsonx.governance (IBM Cloud)
        wxgov_client = WatsonxExternalPromptMonitor(
            api_key="API_KEY", space_id="SPACE_ID"
        )

        # watsonx.governance (CP4D)
        cpd_creds = CloudPakforDataCredentials(
            url="CPD_URL",
            username="USERNAME",
            password="PASSWORD",
            version="5.0",
            instance_id="openshift",
        )

        wxgov_client = WatsonxExternalPromptMonitor(
            space_id="SPACE_ID", cpd_creds=cpd_creds
        )
        ```
    """

    def __init__(
        self,
        api_key: str = None,
        space_id: str = None,
        project_id: str = None,
        region: Union[Region, str] = Region.US_SOUTH,
        cpd_creds: Union[CloudPakforDataCredentials, Dict] = None,
        subscription_id: str = None,
        **kwargs,
    ) -> None:
        import ibm_aigov_facts_client  # noqa: F401
        import ibm_cloud_sdk_core.authenticators  # noqa: F401
        import ibm_watson_openscale  # noqa: F401
        import ibm_watsonx_ai  # noqa: F401

        super().__init__(**kwargs)

        self.space_id = space_id
        self.project_id = project_id
        self.region = Region.from_value(region)
        self.subscription_id = subscription_id
        self._api_key = api_key
        self._wos_client = None

        self._container_id = space_id if space_id else project_id
        self._container_type = "space" if space_id else "project"
        self._deployment_stage = "production" if space_id else "development"

        if cpd_creds:
            self._wos_cpd_creds = validate_and_filter_dict(
                cpd_creds.to_dict(),
                ["username", "password", "api_key", "disable_ssl_verification"],
                ["url"],
            )
            self._fact_cpd_creds = validate_and_filter_dict(
                cpd_creds.to_dict(),
                ["username", "password", "api_key", "bedrock_url"],
                ["url"],
            )
            self._fact_cpd_creds["service_url"] = self._fact_cpd_creds.pop("url")
            self._wml_cpd_creds = validate_and_filter_dict(
                cpd_creds.to_dict(),
                [
                    "username",
                    "password",
                    "api_key",
                    "instance_id",
                    "version",
                    "bedrock_url",
                ],
                ["url"],
            )

    def _create_detached_prompt(
        self,
        detached_details: Dict,
        prompt_template_details: Dict,
        detached_asset_details: Dict,
    ) -> str:
        from ibm_aigov_facts_client import (  # type: ignore
            AIGovFactsClient,
            CloudPakforDataConfig,
            DetachedPromptTemplate,
            PromptTemplate,
        )

        try:
            if hasattr(self, "_fact_cpd_creds") and self._fact_cpd_creds:
                cpd_creds = CloudPakforDataConfig(**self._fact_cpd_creds)

                aigov_client = AIGovFactsClient(
                    container_id=self._container_id,
                    container_type=self._container_type,
                    cloud_pak_for_data_configs=cpd_creds,
                    disable_tracing=True,
                )

            else:
                aigov_client = AIGovFactsClient(
                    api_key=self._api_key,
                    container_id=self._container_id,
                    container_type=self._container_type,
                    disable_tracing=True,
                    region=self.region.factsheet,
                )

        except Exception as e:
            logging.error(
                f"Error connecting to IBM watsonx.governance (factsheets): {e}",
            )
            raise

        created_detached_pta = aigov_client.assets.create_detached_prompt(
            **detached_asset_details,
            prompt_details=PromptTemplate(**prompt_template_details),
            detached_information=DetachedPromptTemplate(**detached_details),
        )

        return created_detached_pta.to_dict()["asset_id"]

    def _create_deployment_pta(self, asset_id: str, name: str, model_id: str) -> str:
        from ibm_watsonx_ai import APIClient, Credentials  # type: ignore

        try:
            if hasattr(self, "_wml_cpd_creds") and self._wml_cpd_creds:
                creds = Credentials(**self._wml_cpd_creds)

                wml_client = APIClient(creds)
                wml_client.set.default_space(self.space_id)

            else:
                creds = Credentials(
                    url=self.region.watsonxai,
                    api_key=self._api_key,
                )
                wml_client = APIClient(creds)
                wml_client.set.default_space(self.space_id)

        except Exception as e:
            logging.error(f"Error connecting to IBM watsonx.ai Runtime: {e}")
            raise

        meta_props = {
            wml_client.deployments.ConfigurationMetaNames.PROMPT_TEMPLATE: {
                "id": asset_id,
            },
            wml_client.deployments.ConfigurationMetaNames.DETACHED: {},
            wml_client.deployments.ConfigurationMetaNames.NAME: name
            + " "
            + "deployment",
            wml_client.deployments.ConfigurationMetaNames.BASE_MODEL_ID: model_id,
        }

        created_deployment = wml_client.deployments.create(asset_id, meta_props)

        return wml_client.deployments.get_uid(created_deployment)

    @deprecated(
        reason="'add_prompt_observer()' is deprecated and will be removed in a future version. Use 'create_prompt_monitor()' instead.",
        version="1.0.5",
        action="always",
    )
    def add_prompt_observer(
        self,
        name: str,
        model_id: str,
        task_id: Literal[
            "extraction",
            "generation",
            "question_answering",
            "retrieval_augmented_generation",
            "summarization",
        ],
        detached_model_provider: str,
        description: str = "",
        model_parameters: Dict = None,
        detached_model_name: str = None,
        detached_model_url: str = None,
        detached_prompt_url: str = None,
        detached_prompt_additional_info: Dict = None,
        prompt_variables: List[str] = None,
        locale: str = "en",
        input_text: str = None,
        context_fields: List[str] = None,
        question_field: str = None,
    ) -> Dict:
        return self.create_prompt_monitor(
            name=name,
            model_id=model_id,
            task_id=task_id,
            detached_model_provider=detached_model_provider,
            description=description,
            model_parameters=model_parameters,
            detached_model_name=detached_model_name,
            detached_model_url=detached_model_url,
            detached_prompt_url=detached_prompt_url,
            detached_prompt_additional_info=detached_prompt_additional_info,
            prompt_variables=prompt_variables,
            locale=locale,
            input_text=input_text,
            context_fields=context_fields,
            question_field=question_field,
        )

    @deprecated(
        reason="'add_prompt_monitor()' is deprecated and will be removed in a future version. Use 'create_prompt_monitor()' instead.",
        version="1.0.6",
        action="always",
    )
    def add_prompt_monitor(
        self,
        name: str,
        model_id: str,
        task_id: Literal[
            "extraction",
            "generation",
            "question_answering",
            "retrieval_augmented_generation",
            "summarization",
        ],
        detached_model_provider: str,
        description: str = "",
        model_parameters: Dict = None,
        detached_model_name: str = None,
        detached_model_url: str = None,
        detached_prompt_url: str = None,
        detached_prompt_additional_info: Dict = None,
        prompt_variables: List[str] = None,
        locale: str = "en",
        input_text: str = None,
        context_fields: List[str] = None,
        question_field: str = None,
    ) -> Dict:
        return self.create_prompt_monitor(
            name=name,
            model_id=model_id,
            task_id=task_id,
            detached_model_provider=detached_model_provider,
            description=description,
            model_parameters=model_parameters,
            detached_model_name=detached_model_name,
            detached_model_url=detached_model_url,
            detached_prompt_url=detached_prompt_url,
            detached_prompt_additional_info=detached_prompt_additional_info,
            prompt_variables=prompt_variables,
            locale=locale,
            input_text=input_text,
            context_fields=context_fields,
            question_field=question_field,
        )

    def create_prompt_monitor(
        self,
        name: str,
        model_id: str,
        task_id: Literal[
            "extraction",
            "generation",
            "question_answering",
            "retrieval_augmented_generation",
            "summarization",
        ],
        detached_model_provider: str,
        description: str = "",
        model_parameters: Dict = None,
        detached_model_name: str = None,
        detached_model_url: str = None,
        detached_prompt_url: str = None,
        detached_prompt_additional_info: Dict = None,
        prompt_variables: List[str] = None,
        locale: str = "en",
        input_text: str = None,
        context_fields: List[str] = None,
        question_field: str = None,
    ) -> Dict:
        """
        Creates a detached (external) prompt template asset and attaches a monitor to the specified prompt template asset.

        Args:
            name (str): The name of the External Prompt Template Asset.
            model_id (str): The ID of the model associated with the prompt.
            task_id (str): The task identifier.
            detached_model_provider (str): The external model provider.
            description (str, optional): A description of the External Prompt Template Asset.
            model_parameters (Dict, optional): Model parameters and their respective values.
            detached_model_name (str, optional): The name of the external model.
            detached_model_url (str, optional): The URL of the external model.
            detached_prompt_url (str, optional): The URL of the external prompt.
            detached_prompt_additional_info (Dict, optional): Additional information related to the external prompt.
            prompt_variables (List[str], optional): Values for the prompt variables.
            locale (str, optional): Locale code for the input/output language. eg. "en", "pt", "es".
            input_text (str, optional): The input text for the prompt.
            context_fields (List[str], optional): A list of fields that will provide context to the prompt.
                Applicable only for "retrieval_augmented_generation" task type.
            question_field (str, optional): The field containing the question to be answered.
                Applicable only for "retrieval_augmented_generation" task type.

        Example:
            ```python
            wxgov_client.create_prompt_monitor(
                name="Detached prompt (model AWS Anthropic)",
                model_id="anthropic.claude-v2",
                task_id="retrieval_augmented_generation",
                detached_model_provider="AWS Bedrock",
                detached_model_name="Anthropic Claude 2.0",
                detached_model_url="https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-claude.html",
                prompt_variables=["context1", "context2", "input_query"],
                input_text="Prompt text to be given",
                context_fields=["context1", "context2"],
                question_field="input_query",
            )
            ```
        """
        if (not (self.project_id or self.space_id)) or (
            self.project_id and self.space_id
        ):
            raise ValueError(
                "Invalid configuration: Neither was provided: please set either 'project_id' or 'space_id'. "
                "Both were provided: 'project_id' and 'space_id' cannot be set at the same time."
            )

        if task_id == "retrieval_augmented_generation":
            if not context_fields or not question_field:
                raise ValueError(
                    "For 'retrieval_augmented_generation' task, requires non-empty 'context_fields' and 'question_field'."
                )

        prompt_metadata = locals()
        # Remove unused vars from dict
        prompt_metadata.pop("self", None)
        prompt_metadata.pop("context_fields", None)
        prompt_metadata.pop("question_field", None)
        prompt_metadata.pop("locale", None)

        # Update name of keys to aigov_facts api
        prompt_metadata["input"] = prompt_metadata.pop("input_text", None)
        prompt_metadata["model_provider"] = prompt_metadata.pop(
            "detached_model_provider",
            None,
        )
        prompt_metadata["model_name"] = prompt_metadata.pop("detached_model_name", None)
        prompt_metadata["model_url"] = prompt_metadata.pop("detached_model_url", None)
        prompt_metadata["prompt_url"] = prompt_metadata.pop("detached_prompt_url", None)
        prompt_metadata["prompt_additional_info"] = prompt_metadata.pop(
            "detached_prompt_additional_info",
            None,
        )

        # Update list of vars to dict
        prompt_metadata["prompt_variables"] = Dict.fromkeys(
            prompt_metadata["prompt_variables"], ""
        )

        from ibm_watson_openscale import APIClient as WosAPIClient  # type: ignore

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

        detached_details = validate_and_filter_dict(
            prompt_metadata,
            ["model_name", "model_url", "prompt_url", "prompt_additional_info"],
            ["model_id", "model_provider"],
        )
        detached_details["prompt_id"] = "detached_prompt_" + str(uuid.uuid4())

        prompt_details = validate_and_filter_dict(
            prompt_metadata,
            ["prompt_variables", "input", "model_parameters"],
        )

        detached_asset_details = validate_and_filter_dict(
            prompt_metadata,
            ["description"],
            ["name", "model_id", "task_id"],
        )

        detached_pta_id = suppress_output(
            self._create_detached_prompt,
            detached_details,
            prompt_details,
            detached_asset_details,
        )
        deployment_id = None
        if self._container_type == "space":
            deployment_id = suppress_output(
                self._create_deployment_pta, detached_pta_id, name, model_id
            )

        monitors = {
            "generative_ai_quality": {
                "parameters": {"min_sample_size": 10, "metrics_configuration": {}},
            },
        }

        max_attempt_execute_prompt_setup = 0
        while max_attempt_execute_prompt_setup < 2:
            try:
                generative_ai_monitor_details = suppress_output(
                    self._wos_client.wos.execute_prompt_setup,
                    prompt_template_asset_id=detached_pta_id,
                    space_id=self.space_id,
                    project_id=self.project_id,
                    deployment_id=deployment_id,
                    label_column="reference_output",
                    context_fields=context_fields,
                    question_field=question_field,
                    operational_space_id=self._deployment_stage,
                    problem_type=task_id,
                    data_input_locale=[locale],
                    generated_output_locale=[locale],
                    input_data_type="unstructured_text",
                    supporting_monitors=monitors,
                    background_mode=False,
                )

                break

            except Exception as e:
                if (
                    e.code == 403
                    and "The user entitlement does not exist" in e.message
                    and max_attempt_execute_prompt_setup < 1
                ):
                    max_attempt_execute_prompt_setup = (
                        max_attempt_execute_prompt_setup + 1
                    )

                    data_marts = self._wos_client.data_marts.list().result
                    if (data_marts.data_marts is None) or (not data_marts.data_marts):
                        raise ValueError(
                            "Error retrieving IBM watsonx.governance (openscale) data mart. \
                                         Make sure the data mart are configured.",
                        )

                    data_mart_id = data_marts.data_marts[0].metadata.id

                    self._wos_client.wos.add_instance_mapping(
                        service_instance_id=data_mart_id,
                        space_id=self.space_id,
                        project_id=self.project_id,
                    )
                else:
                    max_attempt_execute_prompt_setup = 2
                    raise

        generative_ai_monitor_details = generative_ai_monitor_details.result._to_dict()

        return {
            "detached_prompt_template_asset_id": detached_pta_id,
            "deployment_id": deployment_id,
            "subscription_id": generative_ai_monitor_details["subscription_id"],
        }

    def store_payload_records(
        self,
        request_records: List[Dict],
        subscription_id: str = None,
    ) -> List[str]:
        """
        Stores records to the payload logging system.

        Args:
            request_records (List[Dict]): A list of records to be logged, where each record is represented as a dictionary.
            subscription_id (str, optional): The subscription ID associated with the records being logged.

        Example:
            ```python
            wxgov_client.store_payload_records(
                request_records=[
                    {
                        "context1": "value_context1",
                        "context2": "value_context1",
                        "input_query": "What's Beekeeper Framework?",
                        "generated_text": "Beekeeper is a data framework to make AI easier to work with.",
                        "input_token_count": 25,
                        "generated_token_count": 150,
                    }
                ],
                subscription_id="5d62977c-a53d-4b6d-bda1-7b79b3b9d1a0",
            )
            ```
        """
        from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
        from ibm_watson_openscale import APIClient as WosAPIClient
        from ibm_watson_openscale.supporting_classes.enums import (
            DataSetTypes,
            TargetTypes,
        )

        # Expected behavior: Prefer using fn `subscription_id`.
        # Fallback to `self.subscription_id` if `subscription_id` None or empty.
        _subscription_id = subscription_id or self.subscription_id

        if _subscription_id is None or _subscription_id == "":
            raise ValueError(
                "Unexpected value for 'subscription_id': Cannot be None or empty string."
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

        subscription_details = self._wos_client.subscriptions.get(
            _subscription_id,
        ).result
        subscription_details = json.loads(str(subscription_details))

        feature_fields = subscription_details["entity"]["asset_properties"][
            "feature_fields"
        ]

        payload_data_set_id = (
            self._wos_client.data_sets.list(
                type=DataSetTypes.PAYLOAD_LOGGING,
                target_target_id=_subscription_id,
                target_target_type=TargetTypes.SUBSCRIPTION,
            )
            .result.data_sets[0]
            .metadata.id
        )

        payload_data = _convert_payload_format(request_records, feature_fields)

        suppress_output(
            self._wos_client.data_sets.store_records,
            data_set_id=payload_data_set_id,
            request_body=payload_data,
            background_mode=False,
        )

        return [data["scoring_id"] + "-1" for data in payload_data]

    def __call__(self, payload: PayloadRecord) -> None:
        if self.prompt_template:
            template_vars = extract_template_vars(
                self.prompt_template.template, payload.input_text
            )

        if not template_vars:
            self.store_payload_records([payload.model_dump()])
        else:
            self.store_payload_records([{**payload.model_dump(), **template_vars}])


class WatsonxPromptMonitor(PromptMonitor):
    """
    Provides functionality to interact with IBM watsonx.governance for monitoring prompts executed within
    IBM watsonx.ai LLMs.

    Note:
        One of the following parameters is required to create a prompt monitor:
        `project_id` or `space_id`, but not both.

    Attributes:
        api_key (str): The API key for IBM watsonx.governance.
        space_id (str, optional): The space ID in watsonx.governance.
        project_id (str, optional): The project ID in watsonx.governance.
        region (Region, optional): The region where watsonx.governance is hosted when using IBM Cloud.
            Defaults to `us-south`.
        cpd_creds (CloudPakforDataCredentials, optional): The Cloud Pak for Data environment credentials.
        subscription_id (str, optional): The subscription ID associated with the records being logged.

    Example:
        ```python
        from beekeeper.monitors.watsonx import (
            WatsonxPromptMonitor,
            CloudPakforDataCredentials,
        )

        # watsonx.governance (IBM Cloud)
        wxgov_client = WatsonxPromptMonitor(api_key="API_KEY", space_id="SPACE_ID")

        # watsonx.governance (CP4D)
        cpd_creds = CloudPakforDataCredentials(
            url="CPD_URL",
            username="USERNAME",
            password="PASSWORD",
            version="5.0",
            instance_id="openshift",
        )

        wxgov_client = WatsonxPromptMonitor(space_id="SPACE_ID", cpd_creds=cpd_creds)
        ```
    """

    def __init__(
        self,
        api_key: str = None,
        space_id: str = None,
        project_id: str = None,
        region: Union[Region, str] = Region.US_SOUTH,
        cpd_creds: Union[CloudPakforDataCredentials, Dict] = None,
        subscription_id: str = None,
        **kwargs,
    ) -> None:
        import ibm_aigov_facts_client  # noqa: F401
        import ibm_cloud_sdk_core.authenticators  # noqa: F401
        import ibm_watson_openscale  # noqa: F401
        import ibm_watsonx_ai  # noqa: F401

        super().__init__(**kwargs)

        self.space_id = space_id
        self.project_id = project_id
        self.region = Region.from_value(region)
        self.subscription_id = subscription_id
        self._api_key = api_key
        self._wos_client = None

        self._container_id = space_id if space_id else project_id
        self._container_type = "space" if space_id else "project"
        self._deployment_stage = "production" if space_id else "development"

        if cpd_creds:
            self._wos_cpd_creds = validate_and_filter_dict(
                cpd_creds.to_dict(),
                ["username", "password", "api_key", "disable_ssl_verification"],
                ["url"],
            )
            self._fact_cpd_creds = validate_and_filter_dict(
                cpd_creds.to_dict(),
                ["username", "password", "api_key", "bedrock_url"],
                ["url"],
            )
            self._fact_cpd_creds["service_url"] = self._fact_cpd_creds.pop("url")
            self._wml_cpd_creds = validate_and_filter_dict(
                cpd_creds.to_dict(),
                [
                    "username",
                    "password",
                    "api_key",
                    "instance_id",
                    "version",
                    "bedrock_url",
                ],
                ["url"],
            )

    def _create_prompt_template(
        self,
        prompt_template_details: Dict,
        asset_details: Dict,
    ) -> str:
        from ibm_aigov_facts_client import (
            AIGovFactsClient,
            CloudPakforDataConfig,
            PromptTemplate,
        )

        try:
            if hasattr(self, "_fact_cpd_creds") and self._fact_cpd_creds:
                cpd_creds = CloudPakforDataConfig(**self._fact_cpd_creds)

                aigov_client = AIGovFactsClient(
                    container_id=self._container_id,
                    container_type=self._container_type,
                    cloud_pak_for_data_configs=cpd_creds,
                    disable_tracing=True,
                )

            else:
                aigov_client = AIGovFactsClient(
                    api_key=self._api_key,
                    container_id=self._container_id,
                    container_type=self._container_type,
                    disable_tracing=True,
                    region=self.region.factsheet,
                )

        except Exception as e:
            logging.error(
                f"Error connecting to IBM watsonx.governance (factsheets): {e}",
            )
            raise

        created_pta = aigov_client.assets.create_prompt(
            **asset_details,
            input_mode="freeform",
            prompt_details=PromptTemplate(**prompt_template_details),
        )

        return created_pta.to_dict()["asset_id"]

    def _create_deployment_pta(self, asset_id: str, name: str, model_id: str) -> str:
        from ibm_watsonx_ai import APIClient, Credentials  # type: ignore

        try:
            if hasattr(self, "_wml_cpd_creds") and self._wml_cpd_creds:
                creds = Credentials(**self._wml_cpd_creds)

                wml_client = APIClient(creds)
                wml_client.set.default_space(self.space_id)

            else:
                creds = Credentials(
                    url=self.region.watsonxai,
                    api_key=self._api_key,
                )

                wml_client = APIClient(creds)
                wml_client.set.default_space(self.space_id)

        except Exception as e:
            logging.error(f"Error connecting to IBM watsonx.ai Runtime: {e}")
            raise

        meta_props = {
            wml_client.deployments.ConfigurationMetaNames.PROMPT_TEMPLATE: {
                "id": asset_id,
            },
            wml_client.deployments.ConfigurationMetaNames.FOUNDATION_MODEL: {},
            wml_client.deployments.ConfigurationMetaNames.NAME: name
            + " "
            + "deployment",
            wml_client.deployments.ConfigurationMetaNames.BASE_MODEL_ID: model_id,
        }

        created_deployment = wml_client.deployments.create(asset_id, meta_props)

        return wml_client.deployments.get_uid(created_deployment)

    @deprecated(
        reason="'add_prompt_observer()' is deprecated and will be removed in a future version. Use 'create_prompt_monitor()' instead.",
        version="1.0.5",
        action="always",
    )
    def add_prompt_observer(
        self,
        name: str,
        model_id: str,
        task_id: Literal[
            "extraction",
            "generation",
            "question_answering",
            "retrieval_augmented_generation",
            "summarization",
        ],
        description: str = "",
        model_parameters: Dict = None,
        prompt_variables: List[str] = None,
        locale: str = "en",
        input_text: str = None,
        context_fields: List[str] = None,
        question_field: str = None,
    ) -> Dict:
        return self.create_prompt_monitor(
            name=name,
            model_id=model_id,
            task_id=task_id,
            description=description,
            model_parameters=model_parameters,
            prompt_variables=prompt_variables,
            locale=locale,
            input_text=input_text,
            context_fields=context_fields,
            question_field=question_field,
        )

    @deprecated(
        reason="'add_prompt_observer()' is deprecated and will be removed in a future version. Use 'create_prompt_monitor()' instead.",
        version="1.0.6",
        action="always",
    )
    def add_prompt_monitor(
        self,
        name: str,
        model_id: str,
        task_id: Literal[
            "extraction",
            "generation",
            "question_answering",
            "retrieval_augmented_generation",
            "summarization",
        ],
        description: str = "",
        model_parameters: Dict = None,
        prompt_variables: List[str] = None,
        locale: str = "en",
        input_text: str = None,
        context_fields: List[str] = None,
        question_field: str = None,
    ) -> Dict:
        return self.create_prompt_monitor(
            name=name,
            model_id=model_id,
            task_id=task_id,
            description=description,
            model_parameters=model_parameters,
            prompt_variables=prompt_variables,
            locale=locale,
            input_text=input_text,
            context_fields=context_fields,
            question_field=question_field,
        )

    def create_prompt_monitor(
        self,
        name: str,
        model_id: str,
        task_id: Literal[
            "extraction",
            "generation",
            "question_answering",
            "retrieval_augmented_generation",
            "summarization",
        ],
        description: str = "",
        model_parameters: Dict = None,
        prompt_variables: List[str] = None,
        locale: str = "en",
        input_text: str = None,
        context_fields: List[str] = None,
        question_field: str = None,
    ) -> Dict:
        """
        Creates an IBM Prompt Template Asset and ssetup monitor for the given prompt template asset.

        Args:
            name (str): The name of the Prompt Template Asset.
            model_id (str): The ID of the model associated with the prompt.
            task_id (str): The task identifier.
            description (str, optional): A description of the Prompt Template Asset.
            model_parameters (Dict, optional): A dictionary of model parameters and their respective values.
            prompt_variables (List[str], optional): A list of values for prompt input variables.
            locale (str, optional): Locale code for the input/output language. eg. "en", "pt", "es".
            input_text (str, optional): The input text for the prompt.
            context_fields (List[str], optional): A list of fields that will provide context to the prompt.
                Applicable only for the `retrieval_augmented_generation` task type.
            question_field (str, optional): The field containing the question to be answered.
                Applicable only for the `retrieval_augmented_generation` task type.

        Example:
            ```python
            wxgov_client.create_prompt_monitor(
                name="IBM prompt template",
                model_id="ibm/granite-3-2b-instruct",
                task_id="retrieval_augmented_generation",
                prompt_variables=["context1", "context2", "input_query"],
                input_text="Prompt text to be given",
                context_fields=["context1", "context2"],
                question_field="input_query",
            )
            ```
        """
        if (not (self.project_id or self.space_id)) or (
            self.project_id and self.space_id
        ):
            raise ValueError(
                "Invalid configuration: Neither was provided: please set either 'project_id' or 'space_id'. "
                "Both were provided: 'project_id' and 'space_id' cannot be set at the same time."
            )

        if task_id == "retrieval_augmented_generation":
            if not context_fields or not question_field:
                raise ValueError(
                    "For 'retrieval_augmented_generation' task, requires non-empty 'context_fields' and 'question_field'."
                )

        prompt_metadata = locals()
        # Remove unused vars from dict
        prompt_metadata.pop("self", None)
        prompt_metadata.pop("context_fields", None)
        prompt_metadata.pop("question_field", None)
        prompt_metadata.pop("locale", None)

        # Update name of keys to aigov_facts api
        prompt_metadata["input"] = prompt_metadata.pop("input_text", None)

        # Update list of vars to dict
        prompt_metadata["prompt_variables"] = Dict.fromkeys(
            prompt_metadata["prompt_variables"], ""
        )

        from ibm_cloud_sdk_core.authenticators import IAMAuthenticator  # type: ignore
        from ibm_watson_openscale import APIClient as WosAPIClient  # type: ignore

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

        prompt_details = validate_and_filter_dict(
            prompt_metadata,
            ["prompt_variables", "input", "model_parameters"],
        )

        asset_details = validate_and_filter_dict(
            prompt_metadata,
            ["description"],
            ["name", "model_id", "task_id"],
        )

        pta_id = suppress_output(
            self._create_prompt_template, prompt_details, asset_details
        )
        deployment_id = None
        if self._container_type == "space":
            deployment_id = suppress_output(
                self._create_deployment_pta, pta_id, name, model_id
            )

        monitors = {
            "generative_ai_quality": {
                "parameters": {"min_sample_size": 10, "metrics_configuration": {}},
            },
        }

        max_attempt_execute_prompt_setup = 0
        while max_attempt_execute_prompt_setup < 2:
            try:
                generative_ai_monitor_details = suppress_output(
                    self._wos_client.wos.execute_prompt_setup,
                    prompt_template_asset_id=pta_id,
                    space_id=self.space_id,
                    project_id=self.project_id,
                    deployment_id=deployment_id,
                    label_column="reference_output",
                    context_fields=context_fields,
                    question_field=question_field,
                    operational_space_id=self._deployment_stage,
                    problem_type=task_id,
                    data_input_locale=[locale],
                    generated_output_locale=[locale],
                    input_data_type="unstructured_text",
                    supporting_monitors=monitors,
                    background_mode=False,
                ).result

                break

            except Exception as e:
                if (
                    e.code == 403
                    and "The user entitlement does not exist" in e.message
                    and max_attempt_execute_prompt_setup < 1
                ):
                    max_attempt_execute_prompt_setup = (
                        max_attempt_execute_prompt_setup + 1
                    )

                    data_marts = self._wos_client.data_marts.list().result
                    if (data_marts.data_marts is None) or (not data_marts.data_marts):
                        raise ValueError(
                            "Error retrieving IBM watsonx.governance (openscale) data mart. \
                                         Make sure the data mart are configured.",
                        )

                    data_mart_id = data_marts.data_marts[0].metadata.id

                    self._wos_client.wos.add_instance_mapping(
                        service_instance_id=data_mart_id,
                        space_id=self.space_id,
                        project_id=self.project_id,
                    )
                else:
                    max_attempt_execute_prompt_setup = 2
                    raise

        generative_ai_monitor_details = generative_ai_monitor_details._to_dict()

        return {
            "prompt_template_asset_id": pta_id,
            "deployment_id": deployment_id,
            "subscription_id": generative_ai_monitor_details["subscription_id"],
        }

    def store_payload_records(
        self,
        request_records: List[Dict],
        subscription_id: str = None,
    ) -> List[str]:
        """
        Stores records to the payload logging system.

        Args:
            request_records (List[Dict]): A list of records to be logged. Each record is represented as a dictionary.
            subscription_id (str, optional): The subscription ID associated with the records being logged.

        Example:
            ```python
            wxgov_client.store_payload_records(
                request_records=[
                    {
                        "context1": "value_context1",
                        "context2": "value_context1",
                        "input_query": "What's Beekeeper Framework?",
                        "generated_text": "Beekeeper is a data framework to make AI easier to work with.",
                        "input_token_count": 25,
                        "generated_token_count": 150,
                    }
                ],
                subscription_id="5d62977c-a53d-4b6d-bda1-7b79b3b9d1a0",
            )
            ```
        """
        from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
        from ibm_watson_openscale import APIClient as WosAPIClient
        from ibm_watson_openscale.supporting_classes.enums import (
            DataSetTypes,
            TargetTypes,
        )

        # Expected behavior: Prefer using fn `subscription_id`.
        # Fallback to `self.subscription_id` if `subscription_id` None or empty.
        _subscription_id = subscription_id or self.subscription_id

        if _subscription_id is None or _subscription_id == "":
            raise ValueError(
                "Unexpected value for 'subscription_id': Cannot be None or empty string."
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

        subscription_details = self._wos_client.subscriptions.get(
            _subscription_id,
        ).result
        subscription_details = json.loads(str(subscription_details))

        feature_fields = subscription_details["entity"]["asset_properties"][
            "feature_fields"
        ]

        payload_data_set_id = (
            self._wos_client.data_sets.list(
                type=DataSetTypes.PAYLOAD_LOGGING,
                target_target_id=_subscription_id,
                target_target_type=TargetTypes.SUBSCRIPTION,
            )
            .result.data_sets[0]
            .metadata.id
        )

        payload_data = _convert_payload_format(request_records, feature_fields)

        suppress_output(
            self._wos_client.data_sets.store_records,
            data_set_id=payload_data_set_id,
            request_body=payload_data,
            background_mode=False,
        )

        return [data["scoring_id"] + "-1" for data in payload_data]

    def __call__(self, payload: PayloadRecord) -> None:
        if self.prompt_template:
            template_vars = extract_template_vars(
                self.prompt_template.template, payload.input_text
            )

        if not template_vars:
            self.store_payload_records([payload.model_dump()])
        else:
            self.store_payload_records([{**payload.model_dump(), **template_vars}])
