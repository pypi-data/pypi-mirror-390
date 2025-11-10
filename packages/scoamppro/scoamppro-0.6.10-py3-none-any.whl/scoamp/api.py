import json
from typing import Dict, Optional, Union
# from requests.adapters import Retry

from .utils.api_utils import (
    DEFAULT_ENDPOINT,
    PAGE_MAX,
    amp_api_path,
    make_request,
    get_user_agent,
)
from .utils.decrypt import decrypt_aes256gcm
from .utils.error import (
    amp_raise_for_status,
    ScoampBaseError,
)


class AmpApi:
    def __init__(
        self,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        path_prefix: Optional[bool] = True,
        user_agent: Union[Dict, str, None] = None,
        auth_v1: Optional[bool] = True,
    ) -> None:
        """Create a client to interact with the AMP Server via HTTP.

        The client is initialized with some high-level settings used in all requests
        made to the Hub (endpoint, authentication, user agents...).

        Args:
            endpoint (`str`, *optional*):
                amp api server base url. Will default to https://amp.sensecoreapi.cn/. To
                be set if you are using a private server.
            access_key (`str`, *optional*):
                access key.
            secret_key (`str`, *optional*):
                secret key.
            user_agent (`str`, `dict`, *optional*):
                The user agent info in the form of a dictionary or a single string. It will
                be completed with information about the installed packages.
            path_prefix (`bool`, *optional*):
                whether the request url has prefix '/studio/amp/data'
            auth_v1 (`bool`, *optional*):
                whether to use sensecore 1.0 auth.
        """
        self.endpoint = endpoint if endpoint is not None else DEFAULT_ENDPOINT
        self.ak = access_key
        self.sk = secret_key
        self.user_agent = user_agent
        self.path_prefix = path_prefix
        self.auth_v1 = auth_v1

    def _amp_url(self, path: str) -> str:
        path = amp_api_path(path, self.path_prefix)
        return self.endpoint + path

    def _amp_headers(self) -> str:
        return {"user-agent": get_user_agent(self.user_agent)}

    def set_endpoint(self, endpoint: str):
        assert endpoint, "'endpoint' should not be empty"
        self.endpoint = endpoint

    def set_auth_info(self, access_key: str, secret_key: str):
        assert access_key and secret_key, (
            "'access_key' and 'secret_key' should not be empty"
        )
        self.ak = access_key
        self.sk = secret_key

    def set_path_prefix(self, path_prefix: bool):
        self.path_prefix = path_prefix

    def set_auth_v1(self, auth_v1: bool):
        self.auth_v1 = auth_v1

    def get_model_space_info(self, model_space_name: str) -> dict:
        method = "GET"
        rmh_endpoint = self.endpoint.replace("amp", "management")
        url = rmh_endpoint + "/rmh/v1/resources"
        params = {
            "filter": f'resource_type="studio.amp.v1.modelSpace" AND name="{model_space_name}"',
        }

        resp = make_request(
            self.ak,
            self.sk,
            method,
            url,
            params=params,
            headers=self._amp_headers(),
            auth_v1=self.auth_v1,
        )
        amp_raise_for_status(resp)

        rj = resp.json()
        if rj["total_size"] < 1:
            return {}
        else:
            return rj["resources"][0]

    def get_user_info(self) -> dict:
        method = "GET"
        url = self._amp_url("/v1/userSecret")
        params = {}

        resp = make_request(
            self.ak,
            self.sk,
            method,
            url,
            params=params,
            headers=self._amp_headers(),
            auth_v1=self.auth_v1,
        )
        amp_raise_for_status(resp)
        return resp.json()

    def get_user_gitinfo(self) -> dict:
        method = "GET"
        url = self._amp_url("/v1/user/gitinfo")
        params = {
            "access_key": self.ak,
        }

        resp = make_request(
            self.ak,
            self.sk,
            method,
            url,
            params=params,
            headers=self._amp_headers(),
            auth_v1=self.auth_v1,
        )
        amp_raise_for_status(resp)
        r = resp.json()
        enc_secret = r.pop("git_user_secret_encrypted")
        r["git_user_secret"] = decrypt_aes256gcm(self.sk, enc_secret)
        return r

    def create_user_model(self, model_id: str, model_space_name: str) -> dict:
        if model_space_name == "maas-modelspace":
            rid = "/subscriptions/maas-subscription/resourceGroups/maas-resourceGroup/zones/maas-zone/modelSpaces/maas-modelspace"
        else:
            ms = self.get_model_space_info(model_space_name)
            if not ms:
                raise ScoampBaseError(f"invalid model space: {model_space_name}")
            rid = ms["rid"]

        method = "POST"
        url = self._amp_url(f"/v1{rid}/models/create")
        json_body = {"name": model_id, "display_name": model_id}

        resp = make_request(
            self.ak,
            self.sk,
            method,
            url,
            json=json_body,
            headers=self._amp_headers(),
            auth_v1=self.auth_v1,
        )
        amp_raise_for_status(resp)
        return resp.json()

    def list_user_models(self, n: int, s: Optional[str]) -> dict:
        if n == 0:
            return None

        method = "GET"
        url = self._amp_url("/v1/modelSpaces/models")
        params = {"order_by": json.dumps([{"field": "update_time", "order": "des"}])}
        if n > 0:
            params["page.size"] = n
        else:
            params["page.size"] = PAGE_MAX

        if s:
            params["filters"] = json.dumps({"model_name": s})

        resp = make_request(
            self.ak,
            self.sk,
            method,
            url,
            params=params,
            headers=self._amp_headers(),
            auth_v1=self.auth_v1,
        )
        amp_raise_for_status(resp)
        return resp.json()

    def get_user_model_info(self, model_id: str) -> dict:
        method = "GET"
        url = self._amp_url(f"/v1/models/{model_id}")

        resp = make_request(
            self.ak,
            self.sk,
            method,
            url,
            headers=self._amp_headers(),
            auth_v1=self.auth_v1,
        )
        amp_raise_for_status(resp)
        return resp.json()

    def list_user_model_files(
        self, model_id: str, revision: Optional[str] = None
    ) -> list:
        # TODO to be deprecated
        model_info = self.get_user_model_info(model_id)
        subscription_name = model_info["subscription_name"]
        resource_group_name = model_info["resource_group_name"]
        zone = model_info["zone"]
        model_space_name = model_info["model_space_name"]

        method = "GET"
        # TODO simplify server url
        url = self._amp_url(
            f"/v1/subscriptions/{subscription_name}/resourceGroups/{resource_group_name}/"
            f"zones/{zone}/modelSpaces/{model_space_name}/models/{model_id}/files"
        )
        params = {"recursive": True}
        if revision:
            params["ref"] = revision

        resp = make_request(
            self.ak,
            self.sk,
            method,
            url,
            params=params,
            headers=self._amp_headers(),
            auth_v1=self.auth_v1,
        )
        amp_raise_for_status(resp)
        return resp.json()["model_files"]

    def list_public_model_files(
        self, model_id: str, revision: Optional[str] = None
    ) -> list:
        method = "GET"
        url = self._amp_url(f"/v1/public/models/{model_id}/files")
        params = {"recursive": True}
        if revision:
            params["ref"] = revision

        resp = make_request(
            self.ak,
            self.sk,
            method,
            url,
            params=params,
            headers=self._amp_headers(),
            auth_v1=self.auth_v1,
        )
        amp_raise_for_status(resp)
        return resp.json()["model_files"]

    def create_public_model(
        self, model_id: str, display_name: Optional[str] = None
    ) -> dict:
        method = "POST"
        url = self._amp_url("/v1/public/models/create")
        json_body = {"name": model_id, "display_name": display_name or model_id}

        resp = make_request(
            self.ak,
            self.sk,
            method,
            url,
            json=json_body,
            headers=self._amp_headers(),
            auth_v1=self.auth_v1,
        )
        amp_raise_for_status(resp)
        return resp.json()

    # TODO add more details abount meta
    def update_public_model_meta(self, model_id: str, meta: dict) -> dict:
        method = "POST"
        url = self._amp_url(f"/v1/public/models/{model_id}/meta")

        resp = make_request(
            self.ak,
            self.sk,
            method,
            url,
            json=meta,
            headers=self._amp_headers(),
            auth_v1=self.auth_v1,
        )
        amp_raise_for_status(resp)
        return resp.json()

    def download_file(
        self,
        model_id: str,
        file_path: str,
        revision: Optional[str] = None,
        is_public: bool = False,
        zone: Optional[str] = "",
        resume_size: Optional[int] = None,
        allow_redirects: bool = True,
        timeout: Optional[float] = None,
    ):
        method = "GET"
        url = self._amp_url("/v1/download/file")
        params = {
            "model_name": model_id,
            "path": file_path,
            "type": "PUBLICMODEL" if is_public else "MODEL",
        }
        if revision:
            params["ref"] = revision

        if zone:
            params["zone"] = zone

        headers = self._amp_headers()
        if resume_size:
            headers["Range"] = f"bytes={resume_size}-"

        resp = make_request(
            self.ak,
            self.sk,
            method,
            url,
            params=params,
            headers=headers,
            stream=True,
            allow_redirects=allow_redirects,
            timeout=timeout,
            auth_v1=self.auth_v1,
        )
        amp_raise_for_status(resp)
        return resp
