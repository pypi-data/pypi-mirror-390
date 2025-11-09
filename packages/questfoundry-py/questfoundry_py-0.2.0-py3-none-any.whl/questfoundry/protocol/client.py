"""Protocol client for QuestFoundry agent communication"""

import re
import time
import uuid
from collections.abc import Callable, Iterator
from datetime import datetime
from pathlib import Path
from typing import Any

from .conformance import validate_envelope_conformance
from .envelope import Envelope, EnvelopeBuilder
from .file_transport import FileTransport
from .transport import Transport
from .types import HotCold, RoleName, SpoilerPolicy


class ProtocolClient:
    """
    High-level client for QuestFoundry protocol communication.

    Provides convenient methods for sending/receiving envelopes with
    automatic validation and support for request/response patterns.

    Example:
        >>> client = ProtocolClient.from_workspace(workspace_dir, "SR")
        >>> envelope = client.create_envelope(
        ...     receiver="GK",
        ...     intent="hook.create",
        ...     payload_type="hook_card",
        ...     payload_data={"title": "Test Hook"}
        ... )
        >>> client.send(envelope)
        >>> response = client.send_and_wait(envelope, timeout=5.0)
    """

    def __init__(self, transport: Transport, sender_role: RoleName) -> None:
        """
        Initialize protocol client.

        Args:
            transport: Transport implementation to use
            sender_role: Role name for this client (e.g., "SR", "GK")
        """
        self.transport = transport
        self.sender_role = sender_role
        self._subscribers: list[tuple[re.Pattern[str], Callable[[Envelope], None]]] = []

    @classmethod
    def from_workspace(
        cls, workspace_dir: Path | str, sender_role: RoleName
    ) -> "ProtocolClient":
        """
        Create a client using file-based transport in a workspace.

        Args:
            workspace_dir: Path to workspace directory
            sender_role: Role name for this client

        Returns:
            ProtocolClient instance
        """
        workspace_path = (
            Path(workspace_dir) if isinstance(workspace_dir, str) else workspace_dir
        )
        transport = FileTransport(workspace_path)
        return cls(transport, sender_role)

    def create_envelope(
        self,
        receiver: RoleName,
        intent: str,
        payload_type: str,
        payload_data: dict[str, Any],
        hot_cold: HotCold = HotCold.HOT,
        player_safe: bool = True,
        spoilers: SpoilerPolicy = SpoilerPolicy.FORBIDDEN,
        correlation_id: str | None = None,
        reply_to: str | None = None,
        tu: str | None = None,
        snapshot: str | None = None,
        refs: list[str] | None = None,
    ) -> Envelope:
        """
        Create an envelope with sensible defaults.

        Args:
            receiver: Receiving role
            intent: Intent verb (e.g., "scene.write")
            payload_type: Artifact type for payload
            payload_data: Payload data dictionary
            hot_cold: Workspace designation (default: "hot")
            player_safe: Whether safe for Player Narrator (default: True)
            spoilers: Spoiler policy (default: "forbidden")
            correlation_id: Optional correlation ID
            reply_to: Optional message ID this replies to
            tu: Optional TU ID
            snapshot: Optional snapshot reference
            refs: Optional list of referenced artifact IDs

        Returns:
            Constructed envelope
        """
        builder = (
            EnvelopeBuilder()
            .with_protocol("1.0.0")
            .with_id(f"urn:uuid:{uuid.uuid4()}")
            .with_time(datetime.now())
            .with_sender(self.sender_role)
            .with_receiver(receiver)
            .with_intent(intent)
            .with_context(hot_cold, tu=tu, snapshot=snapshot)
            .with_safety(player_safe, spoilers)
            .with_payload(payload_type, payload_data)
        )

        if correlation_id:
            builder = builder.with_correlation_id(correlation_id)
        if reply_to:
            builder = builder.with_reply_to(reply_to)
        if refs:
            builder = builder.with_refs(refs)

        return builder.build()

    def send(self, envelope: Envelope, validate: bool = True) -> None:
        """
        Send an envelope.

        Args:
            envelope: The envelope to send
            validate: Whether to validate conformance (default: True)

        Raises:
            ValueError: If envelope fails conformance validation
            IOError: If sending fails
        """
        if validate:
            result = validate_envelope_conformance(envelope)
            if not result.conformant:
                violations = "\n".join(f"  - {v.message}" for v in result.violations)
                raise ValueError(
                    f"Envelope conformance validation failed:\n{violations}"
                )

        self.transport.send(envelope)

    def receive(self, validate: bool = True) -> Iterator[Envelope]:
        """
        Receive envelopes.

        Args:
            validate: Whether to validate conformance (default: True)

        Yields:
            Envelope: Received envelopes

        Raises:
            IOError: If receiving fails
        """
        for envelope in self.transport.receive():
            if validate:
                result = validate_envelope_conformance(envelope)
                if not result.conformant:
                    # Log warnings but don't block receiving
                    # In production, you might want to handle this differently
                    continue

            # Check subscribers
            for pattern, callback in self._subscribers:
                if pattern.match(envelope.intent):
                    callback(envelope)

            yield envelope

    def send_and_wait(
        self,
        envelope: Envelope,
        timeout: float = 10.0,
        validate: bool = True,
    ) -> Envelope | None:
        """
        Send an envelope and wait for a correlated response.

        Args:
            envelope: The envelope to send
            timeout: Timeout in seconds (default: 10.0)
            validate: Whether to validate conformance (default: True)

        Returns:
            Response envelope if received, None if timeout

        Raises:
            ValueError: If envelope fails conformance validation
            IOError: If sending/receiving fails
        """
        # Ensure envelope has correlation_id
        if not envelope.correlation_id:
            # Create a copy with correlation_id using model_copy
            correlation_id = str(uuid.uuid4())
            envelope = envelope.model_copy(update={"correlation_id": correlation_id})

        # Send the request
        self.send(envelope, validate=validate)

        # Wait for response with matching correlation_id
        start_time = time.time()
        first_iteration = True
        while time.time() - start_time < timeout:
            # Sleep between checks to avoid busy-waiting (except first iteration)
            if not first_iteration:
                time.sleep(0.1)
            first_iteration = False

            for response in self.receive(validate=validate):
                # Match correlation_id but skip the original request
                if (
                    response.correlation_id == envelope.correlation_id
                    and response.id != envelope.id
                ):
                    return response

        return None

    def subscribe(
        self, intent_pattern: str, callback: Callable[[Envelope], None]
    ) -> None:
        r"""
        Subscribe to messages matching an intent pattern.

        The callback will be invoked for each matching message during receive().

        Args:
            intent_pattern: Regex pattern to match intents (e.g., "scene\..*")
            callback: Function to call with matching envelopes
        """
        pattern = re.compile(intent_pattern)
        self._subscribers.append((pattern, callback))

    def unsubscribe_all(self) -> None:
        """Remove all subscriptions."""
        self._subscribers.clear()

    def close(self) -> None:
        """Close the transport and release resources."""
        self.transport.close()

    def __enter__(self) -> "ProtocolClient":
        """Context manager entry"""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Context manager exit"""
        self.close()
