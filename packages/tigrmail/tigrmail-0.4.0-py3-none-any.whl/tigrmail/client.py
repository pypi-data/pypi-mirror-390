from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, TypedDict

from typing_extensions import NotRequired

from .api import ApiClient
from .errors import TigrmailError


class EmailMessage(TypedDict):
    from_: str
    to: List[str]
    subject: str
    body: str


class _SubjectFilter(TypedDict, total=False):
    contains: str
    equals: str


class _FromFilter(TypedDict, total=False):
    email: str
    domain: str


class MessageFilter(TypedDict):
    inbox: str
    subject: NotRequired[_SubjectFilter]
    from_: NotRequired[_FromFilter]


class Tigrmail:
    def __init__(self, *, token: str) -> None:
        self._token = token
        self._api = ApiClient()

    def close(self) -> None:
        self._api.close()

    def create_email_address(self) -> str:
        try:
            resp = self._api.post(
                "/v1/inboxes",
                headers={"Authorization": f"Bearer {self._token}"},
                json=None,
            )
            data = resp.json()
            # expected shape: { "inbox": "..." }
            return data["inbox"]
        except Exception as exc:
            raise TigrmailError(
                error=exc,
                general_message="Failed to generate a new inbox.",
            )

    def poll_next_message(self, *, inbox: str, subject: Optional[Dict[str, str]] = None, from_: Optional[Dict[str, str]] = None) -> EmailMessage:
        try:
            params: Dict[str, str] = {
                "inbox": inbox,
            }
            if subject:
                if "contains" in subject and subject.get("contains"):
                    params["subjectContains"] = subject["contains"]
                if "equals" in subject and subject.get("equals"):
                    params["subjectEquals"] = subject["equals"]
            if from_:
                if "email" in from_ and from_.get("email"):
                    params["fromEmail"] = from_["email"]
                if "domain" in from_ and from_.get("domain"):
                    params["fromDomain"] = from_["domain"]

            # filter out empty/falsey values similar to TS SDK
            params = {k: v for k, v in params.items() if v}

            resp = self._api.get(
                "/v1/messages",
                headers={"Authorization": f"Bearer {self._token}"},
                params=params,
            )
            payload = resp.json()
            msg = payload.get("message", {})
            # Map to python EmailMessage with 'from_' key to avoid keyword
            return EmailMessage(
                from_=msg.get("from", ""),
                to=msg.get("to", []) or [],
                subject=msg.get("subject", ""),
                body=msg.get("body", ""),
            )
        except Exception as exc:
            raise TigrmailError(
                error=exc,
                general_message=f"Failed to poll the next message for inbox: {inbox}.",
            )
