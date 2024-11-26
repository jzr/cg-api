import logging

from enum import Enum
from functools import partialmethod
from typing import Any, Type

import requests
from requests.adapters import HTTPAdapter, Retry

from .configuration import Config, list_profiles

logger = logging.getLogger(__package__)


class Session:
    def __init__(
        self,
        base_url: str = None,
        key: str = None,
        secret: str = None,
        profile_name=None,
    ):
        if base_url and key and secret:
            self.config = configuration.Config(base_url, key, secret)
        elif profile_name:
            self.config = configuration.FileConfigProvider(
                profile_name=profile_name
            ).load()
        else:
            self.config = configuration.load_default()

        if not all(
            hasattr(self.config, attr) for attr in ["BASE_URL", "KEY", "SECRET"]
        ):
            raise TypeError(f"Invalid config: {self.config}")

    # requests wrapper with authentication and minor handling

    def call(
        self,
        endpoint: str,
        data: object = None,
        method: str = "GET",
        raw_response=False,
        **kwargs,
    ):
        session = requests.Session()
        retries = Retry(total=10, backoff_factor=0.5, status_forcelist=[429])
        session.mount("https://", HTTPAdapter(max_retries=retries))

        response = session.request(
            method=method,
            url=f"{self.config.BASE_URL}/{endpoint}",
            json=data,
            auth=(self.config.KEY, self.config.SECRET),
            **kwargs,
        )

        logger.debug("response status_code: %s", response.status_code)
        logger.debug("response headers: %s", response.headers)

        if response.status_code == 401:
            raise RuntimeError(f"401 Authentication failed: {response.text}")
        if response.status_code == 204:
            # No content
            return ""
        if response.status_code < 200 or response.status_code > 300:
            raise RuntimeError(
                f"Unexpected status code: {response.status_code}, {response.text}"
            )
        if raw_response:
            return response
        elif response.headers.get("Content-Type", "").startswith("application/json"):
            return response.json()
        else:
            return response.text

    post = partialmethod(call, method="POST")
    get = partialmethod(call, method="GET")
    put = partialmethod(call, method="PUT")
    delete = partialmethod(call, method="DELETE")
    patch = partialmethod(call, method="PATCH")

    # Helper functions for interactive usage

    def whoami(self):
        me = self.get("user/me")
        return {k: v for k, v in me.items() if k in ["id", "name", "accountId"]}

    def info(self):
        me = self.get("user/me")
        account = self.get("account")
        data = f"{me['name']} ({me['id']}) in '{account['name']}' ({me['accountId']})\n"
        data += (
            f"Plan: {account['plan']}, CloudInfra: {account['cloudInfraTenantId']}\n"
        )
        data += f"Active features: {account['activeFeatures']}"
        print(data)

    def switch_profile(self, profile: str):
        self.config = configuration.FileConfigProvider(profile_name=profile).load()
        print(self.whoami())
