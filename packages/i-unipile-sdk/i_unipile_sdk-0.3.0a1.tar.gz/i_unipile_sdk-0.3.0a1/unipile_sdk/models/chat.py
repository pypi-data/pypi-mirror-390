from __future__ import annotations

from typing import Any, Literal, Union

from pydantic import BaseModel, Field

from .common import AccountType
from .user import ContactInfo


class LinkedinSpecificUserData(BaseModel):
    """
    Provider specific user's additional data for Linkedin.
    """

    provider: Literal["LINKEDIN"]
    member_urn: str
    occupation: str | None = None
    network_distance: (
        Literal["SELF", "DISTANCE_1", "DISTANCE_2", "DISTANCE_3", "OUT_OF_NETWORK"] | None
    ) = None
    pending_invitation: bool | None = None
    location: str | None = None
    headline: str | None = None
    contact_info: ContactInfo | None = None


class ChatAttendee(BaseModel):
    object: Literal["ChatAttendee"]
    id: str = Field(..., description="A unique identifier.", min_length=1, title="UniqueId")
    account_id: str = Field(
        ..., description="A unique identifier.", min_length=1, title="UniqueId"
    )
    provider_id: str
    name: str
    is_self: Literal[0, 1]
    hidden: Literal[0, 1] | None = None
    picture_url: str | None = None
    profile_url: str | None = None
    specifics: LinkedinSpecificUserData | None = Field(
        default=None, description="Provider specific additional data."
    )


class ChatAttendeesResponse(BaseModel):
    object: Literal["ChatAttendeeList"]
    items: list[ChatAttendee]
    cursor: str | None


class Chat(BaseModel):
    object: Literal["Chat"]
    id: str = Field(..., description="A unique identifier.", min_length=1, title="UniqueId")
    account_id: str = Field(
        ..., description="A unique identifier.", min_length=1, title="UniqueId"
    )
    account_type: AccountType
    provider_id: str
    attendee_provider_id: str | None = None

    name: str | None = None
    type: Literal[0, 1, 2]
    timestamp: str
    unread_count: int
    archived: Literal[0, 1]
    muted_until: Literal[-1] | str | None = None
    read_only: Literal[0, 1]
    disabled_features: list[Literal["reactions", "reply"]] | None = Field(
        default=None, alias="disabledFeatures"
    )
    subject: str | None = None
    organization_id: str | None = Field(
        default=None, description="Linkedin specific ID for organization mailboxes."
    )
    mailbox_id: str | None = Field(
        default=None, description="Linkedin specific ID for organization mailboxes."
    )
    content_type: Literal["inmail", "sponsored", "linkedin_offer", "invitation"] | None = None
    folder: (
        list[
            Literal[
                "INBOX",
                "INBOX_LINKEDIN_CLASSIC",
                "INBOX_LINKEDIN_RECRUITER",
                "INBOX_LINKEDIN_SALES_NAVIGATOR",
                "INBOX_LINKEDIN_ORGANIZATION",
            ]
        ]
        | None
    ) = None


class ChatsResponse(BaseModel):
    object: Literal["ChatList"]
    items: list[Chat]
    cursor: Any


class AttachementSize(BaseModel):
    width: float
    height: float


class Attachment(BaseModel):
    id: str
    file_size: float | None
    unavailable: bool
    mimetype: str | None = None
    url: str | None = None
    url_expires_at: float | None = None


class AttachementImg(Attachment):
    type: Literal["img"]
    size: AttachementSize
    sticker: bool


class AttachmentVideo(Attachment):
    type: Literal["video"]
    size: AttachementSize
    gif: bool


class AttachmentAudio(Attachment):
    type: Literal["audio"]
    duration: float | None = None
    voice_note: bool


class AttachmentFile(Attachment):
    type: Literal["file"]
    file_name: str


class AttachmentPost(Attachment):
    type: Literal["linkedin_post"]


class MessageReaction(BaseModel):
    value: str
    sender_id: str
    is_sender: bool


class MessageQuoted(BaseModel):
    provider_id: str
    sender_id: str
    text: Union[str, Any]
    attachments: list[
        Union[AttachementImg, AttachmentVideo, AttachmentAudio, AttachmentFile, AttachmentPost]
    ]


class Message(BaseModel):
    object: Literal["Message"]
    provider_id: str
    sender_id: str
    text: str | None = None
    attachments: list[
        AttachementImg | AttachmentVideo | AttachmentAudio | AttachmentFile | AttachmentPost
    ]
    id: str = Field(
        ..., description="A unique identifier.", min_length=1, title="Unique message id"
    )
    account_id: str = Field(
        ..., description="A unique identifier.", min_length=1, title="Unique account id"
    )
    chat_id: str = Field(
        ..., description="A unique identifier.", min_length=1, title="Unique chat id"
    )
    chat_provider_id: str
    timestamp: str

    is_sender: Literal[0, 1]
    quoted: MessageQuoted | None = None

    reactions: list[MessageReaction]
    seen: Literal[0, 1]
    seen_by: dict[str, Any]
    hidden: Literal[0, 1]
    deleted: Literal[0, 1]
    edited: Literal[0, 1]
    is_event: Literal[0, 1]
    delivered: Literal[0, 1]
    behavior: Literal[0] | Any

    event_type: Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9] | None = None
    original: str
    replies: float | None = None
    reply_by: list[str] | None = None
    parent: str | None = Field(
        default=None, description="A unique parent identifier.", min_length=1
    )
    sender_attendee_id: str = Field(
        description="A unique sender attendee identifier.", min_length=1
    )
    subject: str | None = None


class ChatsMessagesResponse(BaseModel):
    object: Literal["MessageList"]
    items: list[Message]
    cursor: Any


class ChatsSendMessageResponse(BaseModel):
    object: Literal["MessageSent"]
    message_id: str = Field(..., description="The Unipile ID of the newly sent message.")


class ChatsStartedResponse(BaseModel):
    object: Literal["ChatStarted"]
    chat_id: str = Field(..., description="The Unipile ID of the newly started chat.")
    message_id: str = Field(..., description="The Unipile ID of the newly sent message.")
