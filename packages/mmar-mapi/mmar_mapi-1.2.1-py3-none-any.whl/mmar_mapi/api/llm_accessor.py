from typing import Literal

from pydantic import BaseModel


class LLMCallProps(BaseModel, frozen=True):
    entrypoint_key: str = ""
    attempts: int = 1


LCP = LLMCallProps()
ResourceId = str
FileId = str
Attachments = list[list[ResourceId]]


class Message(BaseModel, frozen=True):
    role: Literal["system", "assistant", "user"]
    content: str


class Messages(BaseModel, frozen=True):
    messages: list[Message]


class Payload(Messages, frozen=True):
    attachments: Attachments | None = None

    def with_attachments(self, attachments: Attachments) -> "Payload":
        return self.model_copy(update=dict(attachments=attachments))

    def __repr__(self):
        parts = [f"messages: {len(self.messages)}", self.attachments and "has attachments"]
        payload_pretty = ", ".join(filter(None, parts))
        return f"Payload({payload_pretty})"


class ResponseExt(BaseModel):
    text: str
    resource_id: ResourceId | None = None


RESPONSE_EMPTY = ResponseExt(text="")
Request = str | Messages | Payload


class LLMAccessorAPI:
    def get_entrypoint_keys(self) -> list[str]:
        raise NotImplementedError

    def get_response(self, *, request: Request, props: LLMCallProps = LCP) -> str:
        raise NotImplementedError

    def get_response_ext(self, *, request: Request, props: LLMCallProps = LCP) -> ResponseExt:
        raise NotImplementedError

    def get_embedding(self, *, prompt: str, props: LLMCallProps = LCP) -> list[float] | None:
        raise NotImplementedError
