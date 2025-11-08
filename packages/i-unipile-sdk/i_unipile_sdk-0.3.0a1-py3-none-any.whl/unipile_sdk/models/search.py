from __future__ import annotations

from enum import Enum, IntEnum
from typing import Any, Literal

from pydantic import BaseModel, Field

from .common import (
    Education,
    LastOutreachActivity,
    NetworkDistance,
    Position,
    WorkExperience,
)


class SearchQuery(BaseModel):
    cursor: str | None
    account_id: str
    limit: int | None


class SearchClassicPeople(BaseModel):
    keywords: str
    account_id: str
    limit: int | None


class PeopleSearchResult(BaseModel):
    type: Literal["PEOPLE"]
    id: str
    public_identifier: str | None = None
    public_profile_url: str | None = None
    profile_url: str | None = None
    profile_picture_url: str | None = None
    profile_picture_url_large: str | None = None
    member_urn: str | None = None
    name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    network_distance: NetworkDistance
    location: str | None = None
    industry: str | None = None
    keywords_match: str | None = None
    headline: str | None = None
    connections_count: int | None = None
    pending_invitation: bool | None = None
    can_send_inmail: bool | None = None
    recruiter_candidate_id: str | None = None
    premium: bool | None = None
    open_profile: bool | None = None
    shared_connections_count: int | None = None
    recent_posts_count: int | None = None
    recently_hired: bool | None = None
    mentioned_in_the_news: bool | None = None
    last_outreach_activity: LastOutreachActivity | None = None
    current_positions: list[Position] | None = None
    education: list[Education] | None = None
    work_experience: list[WorkExperience] | None = None


class CompanySearchResult(BaseModel):
    object: Literal["SearchResult"]
    type: Literal["COMPANY"]
    id: str
    name: str
    location: str | None = None
    profile_url: str
    industry: str
    summary: str | None = None
    followers_count: int
    job_offers_count: int
    headcount: str


class LocationParam(BaseModel):
    id: str = Field(min_length=1)
    priority: Literal["CAN_HAVE", "MUST_HAVE", "DOESNT_HAVE"] | None = None
    scope: Literal["CURRENT", "OPEN_TO_RELOCATE_ONLY", "CURRENT_OR_OPEN_TO_RELOCATE"] | None = None


class CompanyParam(BaseModel):
    include: list[str] | None = None
    exclude: list[str] | None = None


class ClassicPeopleSearch(BaseModel):
    api: Literal["classic"]
    category: Literal["people"]
    keywords: str | None = None
    industry: list[str] | None = None
    location: list[str] | None = None
    profile_language: list[str] | None = Field(None, min_length=2, max_length=2)
    network_distance: list[int] | None = Field(None, ge=1, le=3)
    company: list[str] | None = None
    past_company: list[str] | None = None
    school: list[str] | None = None
    service: list[str] | None = None
    connections_of: list[str] | None = None
    followers_of: list[str] | None = None
    open_to: list[Literal["proBono", "boardMember"]] | None = None
    advanced_keywords: dict[str, str] | None = None


class SearchResponse(BaseModel):
    object: Literal["LinkedinSearch"]
    items: list[PeopleSearchResult]
    config: dict[str, Any]  # This could be more specific based on your needs
    paging: dict[str, Any]  # This could be more specific based on your needs
    cursor: str | None = None


class SearchCompanyResponse(BaseModel):
    object: Literal["LinkedinSearch"]
    items: list[CompanySearchResult]
    config: dict[str, Any]  # This could be more specific based on your needs
    paging: dict[str, Any]  # This could be more specific based on your needs
    cursor: str | None = None


class NetworkDistanceEnum(IntEnum):
    FIRST = 1
    SECOND = 2
    THIRD = 3


class OpenToEnum(str, Enum):
    PRO_BONO = "proBono"
    BOARD_MEMBER = "boardMember"


class AdvancedKeywords(BaseModel):
    first_name: str | None = Field(
        default=None, description="Linkedin native filter : KEYWORDS / FIRST NAME."
    )
    last_name: str | None = Field(
        default=None, description="Linkedin native filter : KEYWORDS / LAST NAME."
    )
    title: str | None = Field(
        default=None, description="Linkedin native filter : KEYWORDS / TITLE."
    )
    company: str | None = Field(
        default=None, description="Linkedin native filter : KEYWORDS / COMPANY."
    )
    school: str | None = Field(
        default=None, description="Linkedin native filter : KEYWORDS / LAST NAME."
    )


class LinkedinSearchPayload(BaseModel):
    api: Literal["classic"] = "classic"
    category: Literal["people"] = "people"
    keywords: str | None = Field(default=None, description="Linkedin native filter : KEYWORDS.")
    industry: list[str] | None = Field(
        default=None,
        description="The ID of the parameter. Use type INDUSTRY on the List search parameters route to find out the right ID.\nLinkedin native filter : INDUSTRY.",
        min_length=1,
        # pattern=r"^[0-9]+$",
    )
    location: list[str] | None = Field(
        default=None,
        description="The ID of the parameter. Use type LOCATION on the List search parameters route to find out the right ID.\nLinkedin native filter : LOCATIONS.",
        min_length=1,
        # pattern=r"^[0-9]+$",
    )
    profile_language: list[str] | None = Field(
        default=None,
        description="ISO 639-1 language code.\nLinkedin native filter : PROFILE LANGUAGE.",
        max_length=2,
        min_length=2,
    )
    network_distance: list[NetworkDistanceEnum] | None = Field(
        default=None,
        description="First, second or third+ degree.\nLinkedin native filter : CONNECTIONS.",
    )
    company: list[str] | None = Field(
        default=None,
        description="The ID of the parameter. Use type COMPANY on the List search parameters route to find out the right ID.\nLinkedin native filter : CURRENT COMPANY.",
        min_length=1,
        # pattern="^\\d+$",
    )
    past_company: list[str] | None = Field(
        default=None,
        description="The ID of the parameter. Use type COMPANY on the List search parameters route to find out the right ID.\nLinkedin native filter : PAST COMPANY.",
        min_length=1,
        # pattern="^\\d+$",
    )
    school: list[str] | None = Field(
        default=None,
        description="The ID of the parameter. Use type SCHOOL on the List search parameters route to find out the right ID.\nLinkedin native filter : SCHOOL.",
        min_length=1,
        # pattern="^\\d+$",
    )
    service: list[str] | None = Field(
        default=None,
        description="The ID of the parameter. Use type SERVICE on the List search parameters route to find out the right ID.\nLinkedin native filter : SERVICE CATEGORIES.",
        min_length=1,
        # pattern="^\\d+$",
    )
    connections_of: list[str] | None = Field(
        default=None,
        description="The ID of the parameter. Use type PEOPLE on the List search parameters route to find out the right ID.\nLinkedin native filter : CONNECTIONS OF.",
        min_length=1,
        # pattern="^.+$",
    )
    followers_of: list[str] | None = Field(
        default=None,
        description="The ID of the parameter. Use type PEOPLE on the List search parameters route to find out the right ID.\nLinkedin native filter : FOLLOWERS OF.",
        min_length=1,
        # pattern="^.+$",
    )
    open_to: list[OpenToEnum] | None = Field(
        default=None, description="Linkedin native filter : OPEN TO."
    )
    advanced_keywords: AdvancedKeywords | None = None


class SalesNavPayloadLocation(BaseModel):
    """
    Linkedin native filter : GEOGRAPHY.
    """

    include: list[str] | None = Field(
        default=None,
        description="The ID of the parameter. Use type LOCATION on the List search parameters route to find out the right ID.",
        min_length=1,
        # pattern="^\\d+$",
    )
    exclude: list[str] | None = Field(
        default=None,
        description="The ID of the parameter. Use type LOCATION on the List search parameters route to find out the right ID.",
        min_length=1,
        # pattern="^\\d+$",
    )


class SalesNavPayloadIndustry(BaseModel):
    """
    Linkedin native filter : INDUSTRY.
    """

    include: list[str] | None = Field(
        default=None,
        description="The ID of the parameter. Use type INDUSTRY on the List search parameters route to find out the right ID.",
        min_length=1,
        # pattern="^\\d+$",
    )
    exclude: list[str] | None = Field(
        default=None,
        description="The ID of the parameter. Use type INDUSTRY on the List search parameters route to find out the right ID.",
        min_length=1,
        # pattern="^\\d+$",
    )


class SalesNavPayloadSchool(BaseModel):
    """
    Linkedin native filter : SCHOOL.
    """

    include: list[str] | None = Field(
        default=None,
        description="The ID of the parameter. Use type SCHOOL on the List search parameters route to find out the right ID.",
        min_length=1,
        # pattern="^\\d+$",
    )
    exclude: list[str] | None = Field(
        default=None,
        description="The ID of the parameter. Use type SCHOOL on the List search parameters route to find out the right ID.",
        min_length=1,
        # pattern="^\\d+$",
    )


class SalesNavPayloadCompany(BaseModel):
    """
    Linkedin native filter : CURRENT COMPANY.
    """

    include: list[str] | None = Field(
        default=None,
        description="The ID of the parameter. Use type COMPANY on the List search parameters route to find out the right ID.",
        min_length=1,
        # pattern="^\\d+$",
    )
    exclude: list[str] | None = Field(
        default=None,
        description="The ID of the parameter. Use type COMPANY on the List search parameters route to find out the right ID.",
        min_length=1,
        # pattern="^\\d+$",
    )


class SalesNavPayloadRole(BaseModel):
    """
    Linkedin native filter : CURRENT JOB TITLE.
    """

    include: list[str] | None = Field(
        default=None,
        description="The ID of the parameter. Use type JOB_TITLE on the List search parameters route to find out the right ID.",
        min_length=1,
        # pattern="^\\d+$",
    )
    exclude: list[str] | None = Field(
        default=None,
        description="The ID of the parameter. Use type JOB_TITLE on the List search parameters route to find out the right ID.",
        min_length=1,
        # pattern="^\\d+$",
    )


class TenureMin(float, Enum):
    NUMBER_0 = 0
    NUMBER_1 = 1
    NUMBER_3 = 3
    NUMBER_6 = 6
    NUMBER_10 = 10


class TenureMax(float, Enum):
    NUMBER_1 = 1
    NUMBER_2 = 2
    NUMBER_5 = 5
    NUMBER_10 = 10


class TenureItem(BaseModel):
    min: TenureMin | None = None
    max: TenureMax | None = None


class LinkedinSalesNavSearchPayload(BaseModel):
    api: Literal["sales_navigator"] = "sales_navigator"
    category: Literal["people"] = "people"
    keywords: str | None = Field(default=None, description="Linkedin native filter : KEYWORDS.")
    saved_search_id: str | None = Field(
        default=None,
        description="The ID of the parameter. Use type SAVED_SEARCHES on the List search parameters route to find out the right ID.\nOverrides all other parameters.",
        # pattern="^\\d+$",
    )
    recent_search_id: str | None = Field(
        default=None,
        description="The ID of the parameter. Use type RECENT_SEARCHES on the List search parameters route to find out the right ID.\nOverrides all other parameters.",
        # pattern="^\\d+$",
    )
    location: SalesNavPayloadLocation | None = Field(
        default=None, description="Linkedin native filter : GEOGRAPHY."
    )
    industry: SalesNavPayloadIndustry | None = Field(
        default=None, description="Linkedin native filter : INDUSTRY."
    )
    first_name: str | None = Field(
        default=None, description="Linkedin native filter : FIRST NAME."
    )
    last_name: str | None = Field(default=None, description="Linkedin native filter : LAST NAME.")
    tenure: list[TenureItem] | None = Field(
        default=None, description="Linkedin native filter : YEARS OF EXPERIENCE."
    )
    groups: list[str] | None = Field(
        default=None,
        description="The ID of the parameter. Use type GROUPS on the List search parameters route to find out the right ID.\nLinkedin native filter : GROUPS.",
        min_length=1,
        # pattern="^\\d+$",
    )
    school: SalesNavPayloadSchool | None = Field(
        default=None, description="Linkedin native filter : SCHOOL."
    )
    profile_language: list[str] | None = Field(
        default=None,
        description="ISO 639-1 language code.\nLinkedin native filter : PROFILE LANGUAGE.",
        max_length=2,
        min_length=2,
    )
    company: SalesNavPayloadCompany | None = Field(
        default=None, description="Linkedin native filter : CURRENT COMPANY."
    )
    role: SalesNavPayloadRole | None = Field(
        default=None, description="Linkedin native filter : CURRENT JOB TITLE."
    )
    network_distance: list[NetworkDistanceEnum | Literal["GROUP"]] | None = Field(
        default=None,
        description="First, second, third+ degree or GROUP.\nLinkedin native filter : CONNECTION.",
    )


class LinkedinURLSearchPayload(BaseModel):
    api: Literal["classic"] = "classic"
    category: Literal["people"] = "people"
    url: str = Field(
        description="The URL to search for.",
        min_length=32,
        pattern=r"^https:\/\/www\.linkedin\.com\/(search\/results\/people\/|sales\/search\/people|recruiter\/search)",
    )


class CommonSearchParameter(str, Enum):
    LOCATION = "LOCATION"
    PEOPLE = "PEOPLE"
    COMPANY = "COMPANY"
    SCHOOL = "SCHOOL"
    INDUSTRY = "INDUSTRY"
    SERVICE = "SERVICE"
    JOB_FUNCTION = "JOB_FUNCTION"
    JOB_TITLE = "JOB_TITLE"
    EMPLOYMENT_TYPE = "EMPLOYMENT_TYPE"
    SKILL = "SKILL"


class SalesNavSearchParameter(str, Enum):
    GROUPS = "GROUPS"
    DEPARTMENT = "DEPARTMENT"
    PERSONA = "PERSONA"
    ACCOUNT_LISTS = "ACCOUNT_LISTS"
    LEAD_LISTS = "LEAD_LISTS"
    TECHNOLOGIES = "TECHNOLOGIES"
    SAVED_ACCOUNTS = "SAVED_ACCOUNTS"
    SAVED_SEARCHES = "SAVED_SEARCHES"
    RECENT_SEARCHES = "RECENT_SEARCHES"


class RecruiterSearchParameter(str, Enum):
    GROUPS = "GROUPS"
    DEPARTMENT = "DEPARTMENT"
    HIRING_PROJECTS = "HIRING_PROJECTS"
    SAVED_SEARCHES = "SAVED_SEARCHES"
    SAVED_FILTERS = "SAVED_FILTERS"


class LinkedinSearchParameter(BaseModel):
    object: Literal["LinkedinSearchParameter"]
    id: str = Field(description="A unique identifier.", min_length=1, title="UniqueId")
    title: str
    additional_data: dict[str, Any] | None = None


class Paging(BaseModel):
    page_count: float


class LinkedinSearchParametersResponse(BaseModel):
    object: Literal["LinkedinSearchParametersList"]
    items: list[LinkedinSearchParameter]
    paging: Paging


class SearchResultsPaging(BaseModel):
    start: int = Field(ge=0)
    page_count: int = Field(ge=0)
    total_count: int = Field(ge=0)


class LinkedinCompanyMessaging(BaseModel):
    is_enabled: bool
    id: str | None = None
    entity_urn: str | None = None


class LinkedinCompanyLocation(BaseModel):
    is_headquarter: bool
    country: str | None = None
    city: str | None = None
    postal_code: str | None = Field(default=None, alias="postalCode")
    street: list[str] | None = None
    description: str | None = None
    area: str | None = None


class LinkedinCompanyProfile(BaseModel):
    object: Literal["CompanyProfile"]
    id: str
    name: str
    description: str | None = None
    entity_urn: str
    public_identifier: str
    profile_url: str
    tagline: str | None = None
    followers_count: float | None = None
    is_followable: bool | None = None
    is_employee: bool | None = None
    messaging: LinkedinCompanyMessaging
    claimed: bool
    viewer_permissions: Any  # TODO: use real model here
    organization_type: (
        Literal["PUBLIC_COMPANY"]
        | Literal["EDUCATIONAL"]
        | Literal["SELF_EMPLOYED"]
        | Literal["GOVERNMENT_AGENCY"]
        | Literal["NON_PROFIT"]
        | Literal["SELF_OWNED"]
        | Literal["PRIVATELY_HELD"]
        | Literal["PARTNERSHIP"]
        | Any
    )
    locations: list[LinkedinCompanyLocation] | None = None
    logo: str | None = None
    localized_description: list[dict[str, Any]] | None = None
    localized_name: list[dict[str, Any]] | None = None
    localized_tagline: list[dict[str, Any]] | None = None
    industry: list[str] | None = None
    activities: list[str] | None = None
    employee_count: float | None = None
    employee_count_range: Any | None = None
    website: str | None = None
    foundation_date: str | None = None
    phone: str | None = None
    insights: Any | None = None  # TODO: use real model here
