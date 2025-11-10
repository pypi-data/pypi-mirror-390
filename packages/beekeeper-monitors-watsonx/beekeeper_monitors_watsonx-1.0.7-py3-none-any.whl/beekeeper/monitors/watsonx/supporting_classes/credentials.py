from typing import Any, Dict, Literal, Optional, Union

from pydantic.v1 import BaseModel


class CloudPakforDataCredentials(BaseModel):
    """
    Encapsulates the credentials required for IBM Cloud Pak for Data.

    Attributes:
        url (str): The host URL of the Cloud Pak for Data environment.
        api_key (str, optional): The API key for the environment, if IAM is enabled.
        username (str, optional): The username for the environment.
        password (str, optional): The password for the environment.
        bedrock_url (str, optional): The Bedrock URL. Required only when IAM integration is enabled on CP4D 4.0.x clusters.
        instance_id (str, optional): The instance ID.
        version (str, optional): The version of Cloud Pak for Data.
        disable_ssl_verification (bool, optional): Indicates whether to disable SSL certificate verification.
            Defaults to `True`.
    """

    url: str
    api_key: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    bedrock_url: Optional[str] = None
    instance_id: Optional[Literal["icp", "openshift"]] = None
    version: Optional[str] = None
    disable_ssl_verification: bool = True

    def __init__(
        self,
        url: str,
        api_key: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        bedrock_url: Optional[str] = None,
        instance_id: Optional[Literal["icp", "openshift"]] = None,
        version: Optional[str] = None,
        disable_ssl_verification: bool = True,
    ) -> None:
        super().__init__(
            url=url,
            api_key=api_key,
            username=username,
            password=password,
            bedrock_url=bedrock_url,
            instance_id=instance_id,
            version=version,
            disable_ssl_verification=disable_ssl_verification,
        )

    def to_dict(self) -> Dict[str, Any]:
        cpd_creds = dict([(k, v) for k, v in self.__dict__.items()])  # noqa: C404

        if "instance_id" in cpd_creds and self.instance_id.lower() not in [
            "icp",
            "openshift",
        ]:
            cpd_creds.pop("instance_id")

        return cpd_creds


class IntegratedSystemCredentials(BaseModel):
    """
    Encapsulates the credentials for an Integrated System based on the authentication type.

    Depending on the `auth_type`, only a subset of the properties is required.

    Attributes:
        auth_type (str): The type of authentication. Currently supports "basic" and "bearer".
        username (str, optional): The username for Basic Authentication.
        password (str, optional): The password for Basic Authentication.
        token_url (str, optional): The URL of the authentication endpoint used to request a Bearer token.
        token_method (str, optional): The HTTP method (e.g., "POST", "GET") used to request the Bearer token.
            Defaults to "POST".
        token_headers (Dict, optional): Optional headers to include when requesting the Bearer token.
            Defaults to `None`.
        token_payload (str | dict, optional): The body or payload to send when requesting the Bearer token.
            Can be a string (e.g., raw JSON). Defaults to `None`.
    """

    auth_type: Literal["basic", "bearer"]
    username: Optional[str]  # basic
    password: Optional[str]  # basic
    token_url: Optional[str]  # bearer
    token_method: Optional[str] = "POST"  # bearer
    token_headers: Optional[Dict] = {}  # bearer
    token_payload: Optional[Union[str, Dict]] = None  # bearer

    def __init__(
        self,
        auth_type: Literal["basic", "bearer"],
        username: str = None,
        password: str = None,
        token_url: str = None,
        token_method: str = "POST",
        token_headers: Dict = {},
        token_payload: Union[str, Dict] = None,
    ) -> None:
        if auth_type == "basic":
            if not username or not password:
                raise ValueError(
                    "`username` and `password` are required for auth_type = 'basic'.",
                )
        elif auth_type == "bearer":
            if not token_url:
                raise ValueError(
                    "`token_url` are required for auth_type = 'bearer'.",
                )

        super().__init__(
            auth_type=auth_type,
            username=username,
            password=password,
            token_url=token_url,
            token_method=token_method,
            token_headers=token_headers,
            token_payload=token_payload,
        )

    def to_dict(self) -> Dict:
        integrated_system_creds = {"auth_type": self.auth_type}

        if self.auth_type == "basic":
            integrated_system_creds["username"] = self.username
            integrated_system_creds["password"] = self.password
        elif self.auth_type == "bearer":
            integrated_system_creds["token_info"] = {
                "url": self.token_url,
                "method": self.token_method,
                "headers": self.token_headers,
                "payload": self.token_payload,
            }

        return integrated_system_creds
