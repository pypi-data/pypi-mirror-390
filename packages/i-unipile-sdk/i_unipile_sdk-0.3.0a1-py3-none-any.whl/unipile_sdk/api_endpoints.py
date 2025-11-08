"""
Unipile API endpoints.
"""

# WARN: use ranged limits type

from datetime import datetime
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse

from typing import Annotated
from httpx import URL
from pydantic import StringConstraints

from unipile_sdk.models import account

from .errors import APIResponseError
from .helpers import iterate_paginated_api
from .models import (
    Accounts,
    ChatAttendeesResponse,
    ChatsMessagesResponse,
    ChatsResponse,
    ChatsSendMessageResponse,
    ChatsStartedResponse,
    CommonSearchParameter,
    LinkedinAccountsConnect,
    LinkedinAccountsConnectResponse,
    LinkedinCompanyProfile,
    LinkedinSalesNavSearchPayload,
    LinkedinSearchParametersResponse,
    LinkedinSearchPayload,
    LinkedinSection,
    LinkedinURLSearchPayload,
    LinkedinUserMe,
    LinkedinUserProfile,
    LinkedinUsersInvitePayload,
    LinkedinUsersInviteResponse,
    NetworkDistance,
    NotFoundType,
    SearchResponse,
    UsersRelationsResponse,
)
from .helpers import reminds_url

from .typing import AccountLinkType, AccountProvider, SyncAsync

if TYPE_CHECKING:  # pragma: no cover
    from .client import BaseClient


class Endpoint:
    def __init__(self, parent: "BaseClient") -> None:
        self.parent = parent


class UsersEndpoint(Endpoint):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def connect(
        self,
        payload: LinkedinAccountsConnect,
    ) -> LinkedinAccountsConnectResponse:
        """
        Link to Uniple an account of the given type and provider.

        Endpoint documentation: https://developer.unipile.com/reference/accountscontroller_createaccount
        """

        return LinkedinAccountsConnectResponse(
            **self.parent.request(
                path="accounts",
                method="POST",
                body=payload.model_dump(exclude_none=True),
            )
        )

    def me(
        self,
        account_id = None,
    ) -> LinkedinUserMe:
        """
        Retrieve informations about account owner.

        Endpoint documentation: https://developer.unipile.com/reference/userscontroller_getaccountownerprofile
        """
        return LinkedinUserMe(
            **self.parent.request(
                path="users/me",
                method="GET",
                account_id=account_id
            )
        )

    def retrieve(
        self,
        identifier: Annotated[str, StringConstraints(min_length=1)],
        account_id = None,
        linkedin_section: LinkedinSection | None = None,
    ) -> LinkedinUserProfile:
        """
        Retrieve the profile of a user. Ensure careful implementation of this action and consult
        provider limits and restrictions:
        https://developer.unipile.com/docs/provider-limits-and-restrictions

        Endpoint documentation: https://developer.unipile.com/reference/userscontroller_getprofilebyidentifier
        """

        return LinkedinUserProfile(
            **self.parent.request(
                path=f"users/{identifier}/",  # NOTE: that slash is required, otherwise it will return 301
                method="GET",
                query={"linkedin_sections": linkedin_section.value} if linkedin_section else {},
                account_id=account_id
            )
        )

    def invite(
        self,
        provider_id: Annotated[str, StringConstraints(min_length=1)],
        account_id = None,
    ) -> LinkedinUsersInviteResponse:
        """
        Send an invitation to add someone to your contacts. Ensure careful implementation of this
        action and consult provider limits and restrictions:
        https://developer.unipile.com/docs/provider-limits-and-restrictions

        Endpoint documentation: https://developer.unipile.com/reference/userscontroller_adduserbyidentifier
        """

        payload = LinkedinUsersInvitePayload(
            account_id=self.parent.resolve_account_id(account_id),
            provider_id=provider_id,
        )

        return LinkedinUsersInviteResponse(
            **self.parent.request(
                path="users/invite",
                method="POST",
                body=payload.model_dump(exclude_none=True),
            )
        )

    def relations(
        self,
        account_id = None,
        filter: str | None = None,
        cursor: str | None = None,
        limit: int = 100,
    ) -> UsersRelationsResponse:
        """
        Returns a list of all the relations of an account. Ensure careful implementation of this
        action and consult provider limits and restrictions:
        https://developer.unipile.com/docs/provider-limits-and-restrictions

        Endpoint documentation: https://developer.unipile.com/reference/userscontroller_getrelations
        """
        return UsersRelationsResponse(
            **self.parent.request(
                path="users/relations",
                method="GET",
                query={
                    "filter": filter,
                    "cursor": cursor,
                    "limit": limit,
                },
                account_id=account_id,
            )
        )


class MessagesEndpoint(Endpoint):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def chat_attendees(
        self,
        cursor: str | None = None,
        limit: int = 100,
        account_id = None
    ):
        """
        Returns a list of messaging attendees. Some optional parameters are available to filter the
        results.

        Endpoint documentation: https://developer.unipile.com/reference/chatattendeescontroller_listallattendees
        """
        return ChatAttendeesResponse(
            **self.parent.request(
                path="chat_attendees",
                method="GET",
                query={
                    "cursor": cursor,
                    "limit": limit,
                },
                account_id = account_id,
            )
        )

    # WARN: add befor/after support
    def list_chats_by_attendee(
        self,
        attendee_id: str,
        account_id = None,
        cursor: str | None = None,
        limit: int = 100,
    ):
        """
        Returns a list of chats where a given attendee is involved.

        Endpoint documentation: https://developer.unipile.com/reference/chatattendeescontroller_listchatsbyattendee
        """
        return ChatsResponse(
            **self.parent.request(
                path=f"chat_attendees/{attendee_id}/chats",
                method="GET",
                query={
                    "cursor": cursor,
                    "limit": limit,
                },
                account_id = account_id,
            )
        )

    # WARN: add before/after support
    def messages(
        self,
        chat_id: Annotated[str, StringConstraints(min_length=1)],
        sender_id: Annotated[str, StringConstraints(min_length=1)] | None = None,
        cursor: str | None = None,
        limit: int = 100,
    ):
        """
        Returns a list of chats where a given attendee is involved.

        Endpoint documentation: https://developer.unipile.com/reference/chatattendeescontroller_listchatsbyattendee
        """
        response = self.parent.request(
            path=f"chats/{chat_id}/messages",
            method="GET",
            query={
                "sender_id": sender_id,
                "cursor": cursor,
                "limit": limit,
            },
        )
        return ChatsMessagesResponse(**response)

    def send_message(
        self,
        chat_id: Annotated[str, StringConstraints(min_length=1)],
        text: str | None = None,  # WARN: need to add restrictions here!
        account_id = None,
    ) -> ChatsSendMessageResponse:
        """
        Send a message to the given chat with the possibility to link some attachments.

        NOTE: unipile support thread_id (slack messaging), voice_message and video_message, but we
        don't use it, so required parameters are not implemented.

        Endpoint documentation: https://developer.unipile.com/reference/chatscontroller_sendmessageinchat
        """

        return ChatsSendMessageResponse(
            **self.parent.request(
                path=f"chats/{chat_id}/messages",
                method="POST",
                body={
                    "text": text,
                },
                account_id = account_id,
            )
        )

    def send_message_to_attendees(
        self,
        attendees_ids: list[Annotated[str, StringConstraints(min_length=1)]],
        account_id = None,
        text: str | None = None,
    ) -> ChatsStartedResponse:
        """
        Start a new conversation with one or more attendee. ⚠️ Interactive documentation does not
        work for Linkedin specific parameters (child parameters not correctly applied in snippet),
        the correct format is linkedin[inmail] = true, linkedin[api]...

        Endpoint documentation: https://developer.unipile.com/reference/chatscontroller_startnewchat
        """

        # TODO: add pydantic model
        return ChatsStartedResponse(
            **self.parent.request(
                path="chats",
                method="POST",
                body={
                    "attendees_ids": attendees_ids,
                    "text": text,
                    "account_id": self.parent.resolve_account_id(account_id),
                },
            )
        )


class AccountsEndpoint(Endpoint):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def accounts(self, cursor: str | None = None, limit: int = 100) -> Accounts:
        """
        Returns a list of the accounts linked to Unipile.

        Endpoint documentation: https://developer.unipile.com/reference/accountscontroller_listaccounts
        """
        return Accounts(
            **self.parent.request(
                path="accounts",
                method="GET",
                query={"cursor": cursor, "limit": limit},
            )
        )

    # TODO: add test
    def delete(
        self,
        account_id = None
    ):
        return self.parent.request(
            path=f"accounts/{self.parent.resolve_account_id(account_id)}",
            method="DELETE",
        )

    def duplicate_amount(self, account_type: str = "LINKEDIN") -> int:
        """
        Count duplicate connected accounts
        """

        im_ids = []
        total_duplicates = 0

        for acc in iterate_paginated_api(
            self.accounts,
            limit=250,
            max_total=5000,  # NOTE: We checking only last 5000 accounts for performance reason
        ):
            if acc.type == account_type and acc.connection_params and acc.connection_params.im:
                if acc.connection_params.im.id in im_ids:
                    total_duplicates += 1
                else:
                    im_ids.append(acc.connection_params.im.id)

        return total_duplicates


class HostedEndpoint(Endpoint):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def link(
        self,
        expiries_on: datetime,
        api_url: URL | None = None,
        success_redirect_url: str | None = None,
        failure_redirect_url: str | None = None,
        notify_url: str | None = None,
        name: str | None = None,
        type: AccountLinkType = "create",
        providers: list[AccountProvider] = ["LINKEDIN"],
    ) -> SyncAsync[Any]:
        """
        Create a url which redirect to Unipile's hosted authentication to connect or reconnect an account.

        Endpoint documentation: https://developer.unipile.com/reference/hostedcontroller_requestlink
        """

        if not api_url:
            api_url = str(self.parent.client.base_url)

        expiries_on_str = (
            f"{expiries_on.strftime('%Y-%m-%dT%H:%M:%S')}.{str(expiries_on.microsecond)[:3]}Z"
        )

        # TODO: convert to pydantic model and use model_dump(exclude_unset=True)
        payload = {
            "type": type,
            "providers": providers,
            "api_url": api_url,
            "expiresOn": expiries_on_str,
            "notify_url": notify_url,
            "name": name,
            "success_redirect_url": success_redirect_url,
            "failure_redirect_url": failure_redirect_url,
        }
        payload = {k: v for k, v in payload.items() if v is not None}

        # TODO: return pydantic model
        return self.parent.request(path="hosted/accounts/link", method="POST", body=payload)

    def retrieve(self):
        pass


class SearchEndpoint(Endpoint):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def search(
        self,
        payload: LinkedinSearchPayload | LinkedinSalesNavSearchPayload | LinkedinURLSearchPayload,
        account_id  = None,
        cursor: str | None = None,
        limit: int | None = None,
        max_limit: int = 100,
    ) -> SearchResponse:
        """
        Search people and companies from the Linkedin Classic as well as Sales Navigator APIs.
        Check out our Guide with examples to master LinkedIn search :
        https://developer.unipile.com/docs/linkedin-search

        Endpoint documentation: https://developer.unipile.com/reference/linkedincontroller_search
        """

        # TODO: verify & move into config module
        LINKEDIN_SEARCH_DEFAULT_LEADS_PER_PAGE = 10
        LINKEDIN_SEARCH_SALES_LEADS_PER_PAGE = 25

        if limit and limit > max_limit:
            raise ValueError(
                f"Invalid limit: {limit}. Maximum search limit (session) is {max_limit}"
            )

        is_sales_search = False
        if isinstance(payload, LinkedinSalesNavSearchPayload):
            is_sales_search = True
        elif isinstance(payload, LinkedinURLSearchPayload):
            if payload.url.startswith("https://www.linkedin.com/sales/search"):
                is_sales_search = True

        # Linkedin Classic shouldn't exceed 50.
        if limit and limit > 50 and not is_sales_search:
            raise ValueError(
                f"Invalid limit: {limit}. Maximum normal search limit (session) is 50"
            )

        request_limit = (
            LINKEDIN_SEARCH_SALES_LEADS_PER_PAGE
            if is_sales_search
            else LINKEDIN_SEARCH_DEFAULT_LEADS_PER_PAGE
        )

        if limit:
            if limit > request_limit:
                request_limit = limit

            # Since we filter users, on low limit value required to scrape slightly
            # more users (compensation), if 130% of limit less than 10, use 10
            # this limitation also optimize sales nav search, because its 25 by default
            elif limit * 1.3 < 10:
                request_limit = 10

        body_data = payload.model_dump(exclude_none=True)
        self.parent.logger.info(f"Starting LinkedIn search with body_data: {body_data}")
        response = self.parent.request(
            path="linkedin/search",
            method="POST",
            query={"cursor": cursor, "limit": request_limit},
            body=body_data,
            account_id=account_id
        )

        search_response = SearchResponse(**response)

        # Filter out of network users
        filtered_items = list(
            filter(
                lambda u: u.network_distance != NetworkDistance.OUT_OF_NETWORK,
                search_response.items,
            )
        )
        filtered_items_length = len(search_response.items) - len(filtered_items)
        if filtered_items_length > 0:
            self.parent.logger.info(
                f"Filtered out leads due to being out of network: {filtered_items_length} "
            )
            search_response.items = filtered_items

        # Apply global limit
        if limit and len(search_response.items) > limit:
            self.parent.logger.info(
                f"Limiting leads due to limit param: {len(search_response.items)} to {limit}"
            )
            search_response.items = search_response.items[:limit]

        self.parent.logger.info(
            f"LinkedIn search completed with leads: {len(search_response.items)}"
        )
        return search_response

    def search_param(
        self,
        type: CommonSearchParameter,
        keywords: str,
        account_id = None,
    ) -> LinkedinSearchParametersResponse:
        """
        LinkedIn doesn't accept raw text as search parameters, but IDs. This route will help you
        get the right IDs for your inputs. Check out our Guide with examples to master LinkedIn
            search : https://developer.unipile.com/docs/linkedin-search

        Endpoint documentation: https://developer.unipile.com/reference/linkedincontroller_getsearchparameterslist
        """
        return LinkedinSearchParametersResponse(
            **self.parent.request(
                path="linkedin/search/parameters",
                method="GET",
                query={"type": type.value, "keywords": keywords},
                account_id=account_id
            )
        )

    def retrieve_company(
        self,
        identifier: Annotated[str, StringConstraints(min_length=1)],
        account_id = None,
    ) -> LinkedinCompanyProfile:
        """
        Get a company profile from its name or ID.

        Endpoint documentation: https://developer.unipile.com/reference/linkedincontroller_getcompanyprofile
        """
        return LinkedinCompanyProfile(
            **self.parent.request(
                path=f"linkedin/company/{identifier}",
                method="GET",
                account_id=account_id
            )
        )

    def retrieve_company_id(
        self,
        url_or_name,
        account_id = None
    ) -> str | None:
        url_or_name = url_or_name.strip()
        url_or_name = url_or_name.rstrip("/")
        company_slug = None

        if url_or_name.isnumeric():
            company_slug = url_or_name  # We do double verification, even if id passed!
        elif (
            url_or_name.startswith("https://www.linkedin.com/company/")
            or url_or_name.startswith("https://linkedin.com/company/")
            or url_or_name.startswith("https://linkedin.com/companies/")
        ):
            company_slug = url_or_name.split("/")[-1]

        if company_slug:
            self.parent.logger.info("Getting company id from slug %s", company_slug)
            try:
                company_id = self.retrieve_company(company_slug, account_id=account_id).id
                return str(company_id)
            except APIResponseError as e:
                if e.error and e.error == NotFoundType.ERRORS_RESOURCE_NOT_FOUND:
                    self.parent.logger.info("Company %s not found, skip processing", url_or_name)
                    return
                else:
                    self.parent.logger.warning(f"Failed to get campaign with {e} error")
                    raise
            except Exception as e:
                self.parent.logger.critical(f"Raised unknown exception {e} for {company_slug}")
                return
        else:
            # If name is URL get domain name
            if reminds_url(url_or_name):
                url_or_name = urlparse(url_or_name).netloc

            search_param = self.search_param(
                type=CommonSearchParameter.COMPANY, keywords=url_or_name, account_id=account_id
            )
            if not search_param.items:
                self.parent.logger.info("Company %s not found, skip processing", url_or_name)
                return

            company_id = str(search_param.items[0].id)

        return company_id
