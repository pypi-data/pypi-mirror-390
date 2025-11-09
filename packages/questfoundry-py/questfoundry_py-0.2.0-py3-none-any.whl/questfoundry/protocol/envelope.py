"""Protocol envelope Pydantic models"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .types import HotCold, RoleName, SpoilerPolicy


class Protocol(BaseModel):
    """Protocol version information"""

    model_config = ConfigDict(frozen=True)

    name: str = Field(default="qf-protocol", pattern="^qf-protocol$")
    version: str = Field(
        ...,
        pattern=r"^\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$",
        description="Semantic version string",
    )


class Sender(BaseModel):
    """Message sender information"""

    role: RoleName = Field(..., description="Sending role")
    agent: str | None = Field(
        None, description="Optional human/agent identifier"
    )


class Receiver(BaseModel):
    """Message receiver information"""

    role: RoleName = Field(..., description="Receiving role")


class Context(BaseModel):
    """Message context and traceability"""

    hot_cold: HotCold = Field(..., description="Workspace designation")
    tu: str | None = Field(
        None,
        pattern=r"^TU-\d{4}-\d{2}-\d{2}-[A-Z]{2,4}\d{2}$",
        description="Thematic Unit ID",
    )
    snapshot: str | None = Field(
        None,
        pattern=r"^Cold @ \d{4}-\d{2}-\d{2}$",
        description="Cold snapshot reference",
    )
    loop: str | None = Field(
        None, description="Loop/playbook context"
    )


class Safety(BaseModel):
    """Safety and spoiler policies"""

    player_safe: bool = Field(
        ..., description="Whether content is safe for Player Narrator"
    )
    spoilers: SpoilerPolicy = Field(
        ..., description="Spoiler content policy"
    )


class Payload(BaseModel):
    """Message payload with type and data"""

    type: str = Field(..., description="Payload artifact type")
    data: dict[str, Any] = Field(..., description="Payload data")


class Envelope(BaseModel):
    """Protocol envelope wrapping all messages"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "protocol": {"name": "qf-protocol", "version": "1.0.0"},
                "id": "urn:uuid:550e8400-e29b-41d4-a716-446655440000",
                "time": "2024-01-15T10:30:00Z",
                "sender": {"role": "SR"},
                "receiver": {"role": "SS"},
                "intent": "scene.write",
                "context": {"hot_cold": "hot", "tu": "TU-2024-01-15-TEST01"},
                "safety": {"player_safe": False, "spoilers": "allowed"},
                "payload": {"type": "tu_brief", "data": {}},
            }
        }
    )

    protocol: Protocol = Field(..., description="Protocol metadata")
    id: str = Field(..., min_length=8, description="Unique message ID")
    time: datetime = Field(..., description="Message creation time")
    sender: Sender = Field(..., description="Message sender")
    receiver: Receiver = Field(..., description="Message receiver")
    intent: str = Field(
        ...,
        pattern=r"^[a-z]+([._-][a-z]+)*$",
        description="Intent verb (e.g., scene.write)",
    )
    correlation_id: str | None = Field(
        None, description="Correlation identifier for request/response"
    )
    reply_to: str | None = Field(
        None, description="Message ID this is replying to"
    )
    context: Context = Field(..., description="Message context")
    safety: Safety = Field(..., description="Safety policies")
    payload: Payload = Field(..., description="Message payload")
    refs: list[str] = Field(
        default_factory=list, description="Referenced artifact IDs"
    )


class EnvelopeBuilder:
    """Fluent builder for constructing Envelopes"""

    def __init__(self) -> None:
        self._protocol = Protocol(name="qf-protocol", version="1.0.0")
        self._id: str | None = None
        self._time: datetime | None = None
        self._sender: Sender | None = None
        self._receiver: Receiver | None = None
        self._intent: str | None = None
        self._correlation_id: str | None = None
        self._reply_to: str | None = None
        self._context: Context | None = None
        self._safety: Safety | None = None
        self._payload: Payload | None = None
        self._refs: list[str] = []

    def with_protocol(self, version: str) -> "EnvelopeBuilder":
        """Set protocol version"""
        self._protocol = Protocol(name="qf-protocol", version=version)
        return self

    def with_id(self, message_id: str) -> "EnvelopeBuilder":
        """Set message ID"""
        self._id = message_id
        return self

    def with_time(self, time: datetime) -> "EnvelopeBuilder":
        """Set message time"""
        self._time = time
        return self

    def with_sender(
        self, role: RoleName, agent: str | None = None
    ) -> "EnvelopeBuilder":
        """Set sender"""
        self._sender = Sender(role=role, agent=agent)
        return self

    def with_receiver(self, role: RoleName) -> "EnvelopeBuilder":
        """Set receiver"""
        self._receiver = Receiver(role=role)
        return self

    def with_intent(self, intent: str) -> "EnvelopeBuilder":
        """Set intent"""
        self._intent = intent
        return self

    def with_correlation_id(self, correlation_id: str) -> "EnvelopeBuilder":
        """Set correlation ID"""
        self._correlation_id = correlation_id
        return self

    def with_reply_to(self, reply_to: str) -> "EnvelopeBuilder":
        """Set reply_to"""
        self._reply_to = reply_to
        return self

    def with_context(
        self,
        hot_cold: HotCold,
        tu: str | None = None,
        snapshot: str | None = None,
        loop: str | None = None,
    ) -> "EnvelopeBuilder":
        """Set context"""
        self._context = Context(
            hot_cold=hot_cold, tu=tu, snapshot=snapshot, loop=loop
        )
        return self

    def with_safety(
        self, player_safe: bool, spoilers: SpoilerPolicy
    ) -> "EnvelopeBuilder":
        """Set safety"""
        self._safety = Safety(player_safe=player_safe, spoilers=spoilers)
        return self

    def with_payload(
        self, artifact_type: str, data: dict[str, Any]
    ) -> "EnvelopeBuilder":
        """Set payload"""
        self._payload = Payload(type=artifact_type, data=data)
        return self

    def with_refs(self, refs: list[str]) -> "EnvelopeBuilder":
        """Set references"""
        self._refs = refs
        return self

    def build(self) -> Envelope:
        """Build the envelope (validates all required fields are set)"""
        if not all(
            [
                self._id,
                self._time,
                self._sender,
                self._receiver,
                self._intent,
                self._context,
                self._safety,
                self._payload,
            ]
        ):
            raise ValueError(
                "Missing required fields. Set all required fields before building."
            )

        # Type narrowing assertions for mypy
        assert self._id is not None
        assert self._time is not None
        assert self._sender is not None
        assert self._receiver is not None
        assert self._intent is not None
        assert self._context is not None
        assert self._safety is not None
        assert self._payload is not None

        return Envelope(
            protocol=self._protocol,
            id=self._id,
            time=self._time,
            sender=self._sender,
            receiver=self._receiver,
            intent=self._intent,
            correlation_id=self._correlation_id,
            reply_to=self._reply_to,
            context=self._context,
            safety=self._safety,
            payload=self._payload,
            refs=self._refs,
        )
