from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    title: str
    detail: str | None = None
    instance: str | None = None
    status: int


class BadRequestType(str, Enum):
    ERRORS_INVALID_PARAMETERS = "errors/invalid_parameters"
    ERRORS_MALFORMED_REQUEST = "errors/malformed_request"
    ERRORS_CONTENT_TOO_LARGE = "errors/content_too_large"
    ERRORS_INVALID_URL = "errors/invalid_url"
    ERRORS_TOO_MANY_CHARACTERS = "errors/too_many_characters"
    ERRORS_UNESCAPED_CHARACTERS = "errors/unescaped_characters"
    ERRORS_MISSING_PARAMETERS = "errors/missing_parameters"


class BadRequestResponse(ErrorResponse):
    type: Literal[
        "errors/invalid_parameters",
        "errors/malformed_request",
        "errors/content_too_large",
        "errors/invalid_url",
        "errors/too_many_characters",
        "errors/unescaped_characters",
        "errors/missing_parameters",
    ]
    status: Literal[400]


class UnauthorizedType(str, Enum):
    ERRORS_MISSING_CREDENTIALS = "errors/missing_credentials"
    ERRORS_MULTIPLE_SESSIONS = "errors/multiple_sessions"
    ERRORS_INVALID_CHECKPOINT_SOLUTION = "errors/invalid_checkpoint_solution"
    ERRORS_CHECKPOINT_ERROR = "errors/checkpoint_error"
    ERRORS_INVALID_CREDENTIALS = "errors/invalid_credentials"
    ERRORS_EXPIRED_CREDENTIALS = "errors/expired_credentials"
    ERRORS_INSUFFICIENT_PRIVILEGES = "errors/insufficient_privileges"
    ERRORS_DISCONNECTED_ACCOUNT = "errors/disconnected_account"
    ERRORS_DISCONNECTED_FEATURE = "errors/disconnected_feature"
    ERRORS_INVALID_CREDENTIALS_BUT_VALID_ACCOUNT_IMAP = (
        "errors/invalid_credentials_but_valid_account_imap"
    )
    ERRORS_EXPIRED_LINK = "errors/expired_link"
    ERRORS_WRONG_ACCOUNT = "errors/wrong_account"


class ForbiddenType(str, Enum):
    ERRORS_ACCOUNT_RESTRICTED = "errors/account_restricted"
    ERRORS_INSUFFICIENT_PERMISSIONS = "errors/insufficient_permissions"
    ERRORS_SESSION_MISMATCH = "errors/session_mismatch"
    ERRORS_FEATURE_NOT_SUBSCRIBED = "errors/feature_not_subscribed"
    ERRORS_UNKNOWN_AUTHENTICATION_CONTEXT = "errors/unknown_authentication_context"
    ERRORS_RESOURCE_ACCESS_RESTRICTED = "errors/resource_access_restricted"


class NotFoundType(str, Enum):
    ERRORS_RESOURCE_NOT_FOUND = "errors/resource_not_found"
    ERRORS_INVALID_RESOURCE_IDENTIFIER = "errors/invalid_resource_identifier"


class UnprocessableEntityType(str, Enum):
    ERRORS_INVALID_ACCOUNT = "errors/invalid_account"
    ERRORS_INVALID_RECIPIENT = "errors/invalid_recipient"
    ERRORS_NO_CONNECTION_WITH_RECIPIENT = "errors/no_connection_with_recipient"
    ERRORS_BLOCKED_RECIPIENT = "errors/blocked_recipient"
    ERRORS_UNPROCESSABLE_ENTITY = "errors/unprocessable_entity"
    ERRORS_INVALID_MESSAGE = "errors/invalid_message"
    ERRORS_INVALID_POST = "errors/invalid_post"
    ERRORS_NOT_ALLOWED_INMAIL = "errors/not_allowed_inmail"
    ERRORS_INSUFFICIENT_CREDITS = "errors/insufficient_credits"
    ERRORS_CANNOT_RESEND_YET = "errors/cannot_resend_yet"
    ERRORS_LIMIT_EXCEEDED = "errors/limit_exceeded"
    ERRORS_ALREADY_INVITED_RECENTLY = "errors/already_invited_recently"
    ERRORS_CANNOT_INVITE_ATTENDEE = "errors/cannot_invite_attendee"
    ERRORS_PARENT_MAIL_NOT_FOUND = "errors/parent_mail_not_found"
    ERRORS_INVALID_REPLY_SUBJECT = "errors/invalid_reply_subject"
    ERRORS_INVALID_HEADERS = "errors/invalid_headers"
    ERRORS_SEND_AS_DENIED = "errors/send_as_denied"
    ERRORS_INVALID_FOLDER = "errors/invalid_folder"
    ERRORS_LIMIT_TOO_HIGH = "errors/limit_too_high"
    ERRORS_UNAUTHORIZED = "errors/unauthorized"
    ERRORS_SENDER_REJECTED = "errors/sender_rejected"
    ERRORS_RECIPIENT_REJECTED = "errors/recipient_rejected"
    ERRORS_IP_REJECTED_BY_SERVER = "errors/ip_rejected_by_server"
    ERRORS_PROVIDER_UNREACHABLE = "errors/provider_unreachable"
    ERRORS_ACCOUNT_CONFIGURATION_ERROR = "errors/account_configuration_error"


class TooManyRequestsErrorType(str, Enum):
    ERRORS_TOO_MANY_REQUESTS = "errors/too_many_requests"


class InternalServerErrorType(str, Enum):
    ERRORS_UNEXPECTED_ERROR = "errors/unexpected_error"
    ERRORS_PROVIDER_ERROR = "errors/provider_error"
    ERRORS_AUTHENTICATION_INTENT_ERROR = "errors/authentication_intent_error"


class NotImplementedErrorType(str, Enum):
    ERRORS_FEATURE_NOT_IMPLEMENTED = "errors/feature_not_implemented"


class ServiceUnavailableErrorType(str, Enum):
    ERRORS_NO_CLIENT_SESSION = "errors/no_client_session"
    ERRORS_NO_CHANNEL = "errors/no_channel"
    ERRORS_NO_HANDLER = "errors/no_handler"
    ERRORS_NETWORK_DOWN = "errors/network_down"
    ERRORS_SERVICE_UNAVAILABLE = "errors/service_unavailable"


class RequestTimeoutErrorType(str, Enum):
    ERRORS_REQUEST_TIMEOUT = "errors/request_timeout"


APIErrorTypes = {
    400: BadRequestType,
    401: UnauthorizedType,
    403: ForbiddenType,
    404: NotFoundType,
    422: UnprocessableEntityType,
    429: TooManyRequestsErrorType,
    500: InternalServerErrorType,
    501: NotImplementedErrorType,
    503: ServiceUnavailableErrorType,
    408: RequestTimeoutErrorType,
}
