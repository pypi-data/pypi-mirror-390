"""
Custom type definitions for unipile client.
"""

from typing import Awaitable, TypeVar, Literal

T = TypeVar("T")
SyncAsync = T | Awaitable[T]

AccountLinkType = Literal["create", "reconnect"]
AccountProvider = Literal[
    "*",  # Any provider
    "*:MAILING",  # Any mailing provider
    "*:MESSAGING",  # Any messaging provider
    "LINKEDIN",
    "WHATSAPP",
    "INSTAGRAM",
    "MESSENGER",
    "TELEGRAM",
    "GOOGLE",
    "OUTLOOK",
    "MAIL",
    "TWITTER",
]

