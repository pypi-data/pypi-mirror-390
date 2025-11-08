"""
Synchronous and asynchronous clients for unipile's API.
"""

import json
import logging
from abc import abstractmethod
from dataclasses import dataclass
from os import environ
from types import TracebackType
from typing import Annotated, Any, Self
import httpx
from httpx import Request, Response
from pydantic import StringConstraints

from .models import APIErrorTypes
from .errors import LinkedinLoginError
from .api_endpoints import (
    MessagesEndpoint,
    AccountsEndpoint,
    HostedEndpoint,
    UsersEndpoint,
    SearchEndpoint,
)
from .errors import (
    APIResponseError,
    HTTPResponseError,
    RequestTimeoutError,
)
from .logging import make_console_logger


@dataclass
class ClientOptions:
    """
    Options to configure the client.
    Attributes:
        auth: Bearer token for authentication. If left undefined, the `auth` parameter
            should be set on each request.
        timeout_ms: Number of milliseconds to wait before emitting a
            `RequestTimeoutError`.
        base_url: The root URL for sending API requests. This can be changed to test with
            a mock server.
        log_level: Verbosity of logs the instance will produce. By default, logs are
            written to `stdout`.
        logger: A custom logger.
        unipile_version: unipile version to use.
    """

    auth: str
    base_url: str
    default_account_id: str | None = None
    timeout_ms: int = 60_000
    log_level: int = logging.INFO
    logger: logging.Logger | None = None
    unipile_version: str = "v1"


class BaseClient:
    def __init__(
        self,
        client: httpx.Client | httpx.AsyncClient,
        options: dict[str, Any] | ClientOptions | None = None,
        **kwargs: Any,
    ) -> None:
        if options is None:
            options = ClientOptions(**kwargs)
        elif isinstance(options, dict):
            options = ClientOptions(**options)
        self.logger = options.logger or make_console_logger()
        self.logger.setLevel(options.log_level)
        self.options = options
        self._clients: list[httpx.Client | httpx.AsyncClient] = []
        self.client = client
        self.accounts = AccountsEndpoint(self)
        self.users = UsersEndpoint(self)
        self.hosted = HostedEndpoint(self)
        self.ln_search = SearchEndpoint(self)
        self.messages = MessagesEndpoint(self)

    @property
    def client(self) -> httpx.Client | httpx.AsyncClient:
        return self._clients[-1]

    @client.setter
    def client(self, client: httpx.Client | httpx.AsyncClient) -> None:
        client.base_url = httpx.URL(f"{self.options.base_url}/api/{self.options.unipile_version}/")
        client.timeout = httpx.Timeout(timeout=self.options.timeout_ms / 1_000)
        client.headers = httpx.Headers(
            {
                "User-Agent": "salesloop/comm_client",
                "accept": "application/json",
            }
        )
        if self.options.auth:
            client.headers["X-API-KEY"] = self.options.auth
        self._clients.append(client)

    def _build_request(
        self,
        method: str,
        path: str,
        query: dict[Any, Any] | None = None,
        body: dict[Any, Any] | None = None,
    ) -> Request:
        headers = httpx.Headers()
        self.logger.info(f"{method} {self.client.base_url}{path}")
        self.logger.debug(f"=> {query} -- {body}")
        return self.client.build_request(method, path, params=query, json=body, headers=headers)

    def _parse_response(self, response: Response) -> dict:
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            try:
                body = error.response.json()
                type = APIErrorTypes[response.status_code]

                # NOTE: verify auth with specific error types
                if body["type"] in ("errors/expired_credentials", "errors/disconnected_account"):
                    raise LinkedinLoginError(
                        f"Failed to verify account with response body: {body}"
                    )
                else:
                    raise APIResponseError(response=response, type=type, body=body)
            except json.JSONDecodeError:
                raise HTTPResponseError(error.response)

        body = response.json()
        self.logger.debug(f"=> {body}")
        return body

    @classmethod
    @abstractmethod
    def request(
        cls,
        path: str,
        method: str,
        query: dict[Any, Any] | None = None,
        body: dict[Any, Any] | None = None,
        account_id: str | None = None,
    ) -> dict:
        # noqa
        pass


class Client(BaseClient):
    """
    Synchronous client for unipile's API.
    """

    client: httpx.Client

    def __init__(
        self,
        options: dict[Any, Any] | ClientOptions | None = None,
        client: httpx.Client | None = None,
        **kwargs: Any,
    ) -> None:
        if client is None:
            client = httpx.Client(transport=httpx.HTTPTransport(retries=2))
        super().__init__(client, options, **kwargs)

    def __enter__(self) -> Self:
        self.client = httpx.Client()
        self.client.__enter__()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException],
        exc_value: BaseException,
        traceback: TracebackType | None,
    ) -> None:
        self.client.__exit__(exc_type, exc_value, traceback)
        del self._clients[-1]

    def _verify_connected_account(self, account_id: str) -> None:
        """
        Verify Linkedin account by checking if we have it in unipile database.
        """
        request = self._build_request(
            "GET",
            f"accounts/{account_id}",
        )

        try:
            response = self.client.send(request)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise LinkedinLoginError(f"Failed to verify {account_id} account: {e.response.text}")
        except httpx.TimeoutException:
            raise RequestTimeoutError()

    def close(self) -> None:
        """
        Close the connection pool of the current inner client.
        """

        self.client.close()

    def request(
        self,
        path: str,
        method: str,
        query: dict[Any, Any] | None = None,
        body: dict[Any, Any] | None = None,
        **kwargs: str
    ) -> dict:
        """
        Send an HTTP request.
        """

        # If account_id passed (even None), means we need to generate query
        # with account_id request
        if "account_id" in kwargs:
            if not query:
                query = {}

            # If no account_id passed try to use default one
            if not kwargs["account_id"]:
                query["account_id"] = self.resolve_account_id()

        # Remove empty values
        if query:
            query = {k: v for k, v in query.items() if v is not None}

        # Do actual request
        request = self._build_request(method, path, query, body)

        try:
            response = self.client.send(request)
        except httpx.TimeoutException:
            raise RequestTimeoutError()

        # TODO: implement, Verify that the account is still connected
        # if response.is_error and query and query.get("account_id"):
        #     self._verify_connected_account(query["account_id"])

        return self._parse_response(response)

    def resolve_account_id(self, account_id: str | None = None) -> str:
        """
        Get the account_id, using the default if not provided.
        """
        if not account_id:
            if self.options.default_account_id:
                return self.options.default_account_id

            raise ValueError("account_id is required")

        return account_id


class AsyncClient(BaseClient):
    """
    Asynchronous client for unipile's API.
    """

    client: httpx.AsyncClient

    def __init__(
        self,
        options: dict[str, Any] | ClientOptions | None = None,
        client: httpx.AsyncClient | None = None,
        **kwargs: Any,
    ) -> None:
        if client is None:
            client = httpx.AsyncClient()
        super().__init__(client, options, **kwargs)

    async def __aenter__(self) -> Self:
        self.client = httpx.AsyncClient()
        await self.client.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException],
        exc_value: BaseException,
        traceback: TracebackType | None,
    ) -> None:
        await self.client.__aexit__(exc_type, exc_value, traceback)
        del self._clients[-1]

    async def aclose(self) -> None:
        """
        Close the connection pool of the current inner client.
        """

        await self.client.aclose()

    async def request(
        self,
        path: str,
        method: str,
        query: dict[Any, Any] | None = None,
        body: dict[Any, Any] | None = None,
        auth: str | None = None,
    ) -> Any:
        """
        Send an HTTP request asynchronously.
        """

        request = self._build_request(method, path, query, body, auth)
        try:
            response = await self.client.send(request)
        except httpx.TimeoutException:
            raise RequestTimeoutError()
        return self._parse_response(response)
