from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class LinkedinSection(str, Enum):
    EXPERIENCE = "experience"
    EDUCATION = "education"
    LANGUAGES = "languages"
    SKILLS = "skills"
    CERTIFICATIONS = "certifications"
    ABOUT = "about"
    VOLUNTEERING_EXPERIENCE = "volunteering_experience"
    PROJECTS = "projects"
    RECOMMENDATIONS_RECEIVED = "recommendations_received"
    RECOMMENDATIONS_GIVEN = "recommendations_given"


class Social(BaseModel):
    type: str
    name: str


class ContactInfo(BaseModel):
    emails: list[str] | None = None
    phones: list[str] | None = None
    adresses: list[str] | None = None
    socials: list[Social] | None = None


class Birthdate(BaseModel):
    month: float
    day: float


class PrimaryLocale(BaseModel):
    country: str
    language: str


class WorkExperienceItem(BaseModel):
    position: str
    company_id: str | None = None
    company: str
    location: str | None = None
    description: str | None = None
    skills: list[str]
    current: bool | None = None
    status: str | None = None
    start: str | Any
    end: str | Any


class VolunteeringExperienceItem(BaseModel):
    company: str
    description: str
    role: str
    cause: str
    start: str | Any
    end: str | Any


class EducationItem(BaseModel):
    degree: str | None = None
    school: str
    field_of_study: str | None = None
    start: str | Any
    end: str | Any


class Skill(BaseModel):
    name: str
    endorsement_count: float
    endorsement_id: float | Any
    insights: list[str]
    endorsed: bool


class Language(BaseModel):
    name: str
    proficiency: str | None = None


class Certification(BaseModel):
    name: str
    organization: str
    url: str | None = None


class Project(BaseModel):
    name: str
    description: str
    skills: list[str]
    start: str | Any
    end: str | Any


class Invitation(BaseModel):
    type: Literal["SENT"] | Literal["RECEIVED"]
    status: Literal["PENDING"] | Literal["IGNORED"] | Literal["WITHDRAWN"]


class LinkedinUserProfile(BaseModel):
    provider: Literal["LINKEDIN"]
    provider_id: str
    public_identifier: str | Any
    first_name: str | Any
    last_name: str | Any
    headline: str
    summary: str | None = None
    contact_info: ContactInfo | None = None
    birthdate: Birthdate | None = None
    primary_locale: PrimaryLocale | None = None
    location: str | None = None
    websites: list[str]
    profile_picture_url: str | None = None
    profile_picture_url_large: str | None = None
    background_picture_url: str | None = None
    hashtags: list[str] | None = None
    can_send_inmail: bool | None = None
    is_open_profile: bool | None = None
    is_premium: bool | None = None
    is_influencer: bool | None = None
    is_creator: bool | None = None
    is_hiring: bool | None = None
    is_open_to_work: bool | None = None
    is_saved_lead: bool | None = None
    is_crm_imported: bool | None = None
    is_relationship: bool | None = None
    is_self: bool | None = None
    invitation: Invitation | None = None
    work_experience: list[WorkExperienceItem] | None = None
    volunteering_experience: list[VolunteeringExperienceItem] | None = None
    education: list[EducationItem] | None = None
    skills: list[Skill] | None = None
    languages: list[Language] | None = None
    certifications: list[Certification] | None = None
    projects: list[Project] | None = None
    follower_count: float | None = None
    connections_count: float | None = None
    shared_connections_count: float | None = None
    network_distance: (
        Literal["FIRST_DEGREE", "SECOND_DEGREE", "THIRD_DEGREE", "OUT_OF_NETWORK"] | None
    ) = None
    public_profile_url: str | None = None
    object: Literal["UserProfile"]


class UsersRelationsResponse(BaseModel):
    object: Literal["UserRelationsList"]
    items: list[UserRelation]
    cursor: Any


class UserRelation(BaseModel):
    object: Literal["UserRelation"]
    first_name: str
    last_name: str
    headline: str
    public_identifier: str
    public_profile_url: str
    created_at: float
    member_id: str
    member_urn: str
    connection_urn: str
    profile_picture_url: str | None = None


class LinkedinUserPlanDisconnected(BaseModel):
    error: Literal["DISCONNECTED"]


class LinkedinUserOrganization(BaseModel):
    id: str
    mailbox_id: str
    name: str


class LinkedinUserPlanInfo(BaseModel):
    owner_seat_id: str
    contract_id: str


class LinkedinUserMe(BaseModel):
    provider: Literal["LINKEDIN"]
    provider_id: str
    entity_urn: str
    object_urn: str
    first_name: str
    last_name: str
    profile_picture_url: str | None = None
    public_profile_url: str | None = None
    public_identifier: str | None = None
    headline: str | None = None
    location: str | None = None
    email: str
    premium: bool
    open_profile: bool
    occupation: str | None = None
    organizations: list[LinkedinUserOrganization | None]
    recruiter: LinkedinUserPlanInfo | LinkedinUserPlanDisconnected | None = None
    sales_navigator: LinkedinUserPlanInfo | LinkedinUserPlanDisconnected | None = None
    object: Literal["AccountOwnerProfile"]

class LinkedinUsersInvitePayload(BaseModel):
    provider_id: str = Field(
        ..., description="The id of the user to add. It has to be the provider’s id."
    )
    account_id: str = Field(..., description="The id of the account where the user will be added.")
    user_email: str | None = Field(
        default=None,
        description="The email address of the user when it\'s required (Linkedin specific).",
    )
    message: str | None = Field(
        default=None,
        description="An optional message to go with the invitation (max 300 chars).",
        # max_length=300, # WARN: are we able to hande this on our side?
    )


class LinkedinUsersInviteResponse(BaseModel):
    object: Literal["UserInvitationSent"]
    invitation_id: str
    usage: float | None = Field(
        default=None,
        description="A percentage of query usage based on the limit set by the"
        "provider. Triggers only on passing a new landing "
        "(50, 75, 90, 95).",
    )
