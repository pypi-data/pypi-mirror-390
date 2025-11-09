from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class AccountType(str, Enum):
    LINKEDIN = "LINKEDIN"
    WHATSAPP = "WHATSAPP"
    SLACK = "SLACK"
    TWITTER = "TWITTER"
    MESSENGER = "MESSENGER"
    INSTAGRAM = "INSTAGRAM"
    TELEGRAM = "TELEGRAM"


class ApiType(str, Enum):
    CLASSIC = "classic"
    SALES_NAVIGATOR = "sales_navigator"
    RECRUITER = "recruiter"
    PREMIUM = "premium"


class CategoryType(str, Enum):
    PEOPLE = "people"
    COMPANIES = "companies"
    POSTS = "posts"
    JOBS = "jobs"


class NetworkDistance(str, Enum):
    SELF = "SELF"
    DISTANCE_1 = "DISTANCE_1"
    DISTANCE_2 = "DISTANCE_2"
    DISTANCE_3 = "DISTANCE_3"
    OUT_OF_NETWORK = "OUT_OF_NETWORK"


class CursorParam(BaseModel):
    cursor: str = Field(min_length=1)


class DateRange(BaseModel):
    year: int | None = None
    month: int | None = None


class TenureInfo(BaseModel):
    years: int | None = None
    months: int | None = None


class Position(BaseModel):
    company: str
    company_id: str | None = None
    description: str | None = None
    role: str
    location: str | None = None
    tenure_at_role: TenureInfo | None = None
    tenure_at_company: TenureInfo | None = None
    start: DateRange | None = None
    end: DateRange | None = None


class Education(BaseModel):
    degree: str | None = None
    school: str
    school_id: str | None = None
    start: DateRange
    end: DateRange | None = None


class WorkExperience(BaseModel):
    company: str
    company_id: str | None = None
    role: str
    industry: str | None = None
    start: DateRange
    end: DateRange | None = None


class Author(BaseModel):
    public_identifier: str
    name: str
    is_company: bool


class LastOutreachActivity(BaseModel):
    type: Literal["SEND_MESSAGE", "ACCEPT_INVITATION"]
    performed_at: str
