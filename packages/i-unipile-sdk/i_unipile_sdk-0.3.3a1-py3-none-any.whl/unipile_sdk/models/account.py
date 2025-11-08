from __future__ import annotations

from enum import Enum
from typing import Any, Literal, Union

from pydantic import BaseModel, Field

from .common import ApiType


class DisabledFeature(str, Enum):
    LINKEDIN_RECRUITER = "linkedin_recruiter"
    LINKEDIN_SALES_NAVIGATOR = "linkedin_sales_navigator"
    LINKEDIN_ORGANIZATIONS_MAILBOXES = "linkedin_organizations_mailboxes"


class AccountSource(BaseModel):
    id: str
    status: Union[
        Literal["OK"],
        Literal["STOPPED"],
        Literal["ERROR"],
        Literal["CREDENTIALS"],
        Literal["PERMISSIONS"],
        Literal["CONNECTING"],
    ] = Field(..., title="AccountSourceServiceStatus")


class AccountSignature(BaseModel):
    title: str
    content: str


class LinkedinAccountOrganization(BaseModel):
    name: str
    messaging_enabled: bool
    organization_urn: str
    mailbox_urn: str


class LinkedinAccountIM(BaseModel):
    id: str
    username: str
    publicIdentifier: str | None = None
    premium_id: Union[str, Any] = Field(..., alias="premiumId")
    premium_contract_id: Union[str, Any] = Field(..., alias="premiumContractId")
    premium_features: list[ApiType] | None = Field(default=None, alias="premiumFeatures")
    organizations: list[LinkedinAccountOrganization]
    proxy: None | Any = None


class LinkedinAccountConnectionParams(BaseModel):
    im: LinkedinAccountIM


class LinkedinAccount(BaseModel):
    object: Literal["Account"]
    type: Literal["LINKEDIN"]
    connection_params: LinkedinAccountConnectionParams
    id: str = Field(..., description="A unique identifier.", min_length=1, title="UniqueId")
    name: str
    created_at: str = Field(
        ...,
        description="An ISO 8601 UTC datetime (YYYY-MM-DDTHH:MM:SS.sssZ). ⚠️ All links expire upon daily restart, regardless of their stated expiration date. A new link must be generated each time a user clicks on your app to connect.",
        examples=["2025-12-31T23:59:59.999Z"],
        # pattern="^[1-2]\d{3}-[0-1]\d-[0-3]\dT\d{2}:\d{2}:\d{2}.\d{3}Z$",
    )
    current_signature: str | None = Field(
        default=None, description="A unique identifier.", min_length=1, title="UniqueId"
    )
    signatures: list[AccountSignature] | None = None
    groups: list[str]
    sources: list[AccountSource]


class Accounts(BaseModel):
    object: Literal["AccountList"]
    items: list[LinkedinAccount]  # NOTE: we might add new types in future
    cursor: str | None = None
    limit: int | None = None


class LinkedinAccountsConnect(BaseModel):
    """
    Authenticate using cookies
    """

    user_agent: str = Field(
        description='If encountering disconnection issues, enter the exact user agent of the browser on which the account has been connected. You can easily retrieve it in the browser\'s console with this command : "console.log(navigator.userAgent)"',
    )
    access_token: str = Field(
        description='Linkedin access token, which is to be found under the key "li_at".',
    )
    premium_token: str | None = Field(
        default=None,
        description='Linkedin Recruiter/Sales Navigator authentication cookie, which is to be found under the key "li_a". It should be used if you need to be logged to an existing session. It not provided, a new session will be started.',
    )

    recruiter_contract_id: str | None = Field(
        default=None,
        description="The contract that should be used with Linkedin Recruiter.",
    )

    country: str | None = Field(
        default=None,
        description="An ISO 3166-1 A-2 country code to be set as proxy's location.",
        max_length=2,
        min_length=2,
    )
    ip: str | None = Field(default=None, description="An IPv4 address to infer proxy's location.")
    disabled_features: list[DisabledFeature] | None = Field(
        default=None,
        description="An array of features that should be disabled for this account.",
    )
    sync_limit: Any | None = Field(  # NOTE: here can be used real model
        default=None,
        description="Set a sync limit either for chats, messages or both. Chats limit will apply to each inbox, whereas messages limit will apply to each chat. No value will not apply any limit (default behaviour). Providers partial support.",
    )
    provider: Literal["LINKEDIN"] = "LINKEDIN"
    proxy: Any | None = None  # NOTE: here can be used real model


class LinkedinAccountsConnectResponse(BaseModel):
    object: Literal["AccountCreated"]
    account_id: str = Field(description="A unique identifier.", min_length=1, title="UniqueId")
