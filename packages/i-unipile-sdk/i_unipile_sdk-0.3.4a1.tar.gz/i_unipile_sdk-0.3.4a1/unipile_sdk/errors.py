"""Custom exceptions for notion-sdk-py.

This module defines the exceptions that can be raised when an error occurs.
"""

from typing import Any

import httpx


class RequestTimeoutError(Exception):
    """Exception for requests that timeout.

    The request that we made waits for a specified period of time or maximum number of
    retries to get the response. But if no response comes within the limited time or
    retries, then this Exception is raised.
    """

    code = "notionhq_client_request_timeout"

    def __init__(self, message: str = "Request to Unipile API has timed out") -> None:
        super().__init__(message)


class HTTPResponseError(Exception):
    """Exception for HTTP errors.

    Responses from the API use HTTP response codes that are used to indicate general
    classes of success and error.
    """

    status: int
    headers: httpx.Headers
    body: str

    def __init__(self, response: httpx.Response, message: str | None = None) -> None:
        if message is None:
            message = f"Request to Unipile API failed with status: {response.status_code}"
        super().__init__(message)
        self.status = response.status_code
        self.headers = response.headers
        self.body = response.text


class APIResponseError(HTTPResponseError):
    """
    An detailed error raised by Unipile API.
    """

    def __init__(
        self,
        response: httpx.Response,
        type: Any,
        body: dict,
    ) -> None:
        super().__init__(response, body["detail"])
        self.title = body.get("title")
        self.instance = body.get("instance")
        self.error = type(body["type"])


class NoIdentifierToRetriveUser(Exception):
    """
    No identifier provided to retrieve user.
    """

    pass


class LinkedinLoginError(Exception):
    """
    An error related to Linkedin login.
    """

    pass