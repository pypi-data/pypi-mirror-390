"""WebSocket client for real-time communication with sandbox containers."""

import asyncio
import json
import secrets
import ssl
from typing import Optional, Dict, Callable, Union
from dataclasses import dataclass
import websockets
from websockets.client import WebSocketClientProtocol

from .types import (
    WebSocketRequestPayload,
    WebSocketResponsePayload,
    RunLongRunningCommandRequest,
    EvalSmallCodeSnippetRequest,
    HealthPingRequest,
    RunLongRunningCommandResponse,
    EvalSmallCodeSnippetResponse,
    HealthPingResponse,
    StreamLongRunningTaskEventResponse,
    ContainerServerReadyResponse,
    StreamLongRunningTaskEventIoDetails,
    StreamLongRunningTaskEventCloseDetails,
)


@dataclass
class StreamingTaskHandler:
    """Handler for streaming task events."""
    on_stdout: Optional[Callable[[str], None]] = None
    on_stderr: Optional[Callable[[str], None]] = None
    on_close: Optional[Callable[[int], None]] = None


@dataclass
class PendingRequest:
    """Pending request waiting for response."""
    future: asyncio.Future
    timeout_handle: Optional[asyncio.TimerHandle] = None


class SandboxWebSocket:
    """WebSocket client for sandbox container communication.

    This class handles:
    - Connection management with automatic reconnection
    - Request-response pattern with message ID tracking
    - Event-based messaging for streaming tasks
    - Health ping to keep connections alive
    - Message queuing when disconnected
    """

    def __init__(self, url: str, token: str) -> None:
        """Initialize WebSocket client.

        Args:
            url: WebSocket URL (e.g., wss://subdomain-13372.run-code.com)
            token: Authentication token for the container
        """
        self.url = url
        self.token = token
        self.ws: Optional[WebSocketClientProtocol] = None
        self.connection_state: str = "disconnected"
        self.should_auto_reconnect: bool = True
        self.message_queue: list[str] = []

        # Message tracking
        self.pending_requests: Dict[str, PendingRequest] = {}
        self.event_waiters: Dict[str, PendingRequest] = {}
        self.streaming_handlers: Dict[str, StreamingTaskHandler] = {}
        self._timeout_tasks: Dict[str, asyncio.Task] = {}
        self._event_timeout_tasks: Dict[str, asyncio.Task] = {}

        # Health ping
        self.health_ping_task: Optional[asyncio.Task] = None
        self.receive_task: Optional[asyncio.Task] = None

    async def connect(self) -> None:
        """Establish WebSocket connection to the container.

        Raises:
            Exception: If connection fails
        """
        if self.connection_state == "connected":
            return

        self.connection_state = "connecting"
        ws_url = f"{self.url}?token={self.token}"

        try:
            # Create SSL context that allows connection even with certificate issues
            # This is needed for development/testing environments
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            self.ws = await websockets.connect(ws_url, ssl=ssl_context)
            self.connection_state = "connected"

            # Start background tasks
            self.receive_task = asyncio.create_task(self._receive_messages())
            self._flush_message_queue()
            self._start_health_ping()

        except Exception as e:
            self.connection_state = "disconnected"
            raise Exception(f"Failed to connect to WebSocket: {e}")

    async def disconnect(self) -> None:
        """Disconnect from the container and clean up resources."""
        self.should_auto_reconnect = False
        await self._cleanup()

    def disable_ws_auto_reconnect(self) -> None:
        """Disable automatic WebSocket reconnection."""
        self.should_auto_reconnect = False

    def is_connected(self) -> bool:
        """Check if WebSocket is currently connected.

        Returns:
            True if connected, False otherwise
        """
        return self.connection_state == "connected"

    async def send(
        self,
        payload: Union[Dict[str, Union[str, int, float, bool, None, Dict, list]], WebSocketRequestPayload],
        timeout: float = 30.0
    ) -> Dict[str, Union[str, int, float, bool, None, Dict, list]]:
        """Send a message to the container and wait for response.

        Args:
            payload: The message payload to send (dict with 'payload' key or WebSocketRequestPayload)
            timeout: Timeout in seconds (default: 30.0)

        Returns:
            Response payload as dict

        Raises:
            asyncio.TimeoutError: If request times out
            Exception: If not connected
        """
        if not self.is_connected():
            raise Exception("WebSocket is not connected")

        # Handle payload wrapper - if it's a dict with 'payload' key, extract it
        # Otherwise, treat it as the payload itself
        if isinstance(payload, dict) and "payload" in payload:
            payload_dict = payload["payload"]
        elif hasattr(payload, 'model_dump'):
            payload_dict = payload.model_dump(by_alias=True)
        else:
            payload_dict = payload

        message_id = self._generate_message_id()
        message = {
            "messageId": message_id,
            "payload": payload_dict
        }

        # Create future for response
        future: asyncio.Future[Dict[str, Union[str, int, float, bool, None, Dict, list]]] = asyncio.Future()

        # Set timeout using asyncio
        async def timeout_handler() -> None:
            await asyncio.sleep(timeout)
            if message_id in self.pending_requests:
                del self.pending_requests[message_id]
                if not future.done():
                    event_type = payload_dict.get('eventType', 'unknown')
                    future.set_exception(
                        asyncio.TimeoutError(f"Request timeout for {event_type}")
                    )

        timeout_task = asyncio.create_task(timeout_handler())

        self.pending_requests[message_id] = PendingRequest(
            future=future,
            timeout_handle=None  # We'll cancel the task instead
        )
        # Store the timeout task separately
        self._timeout_tasks[message_id] = timeout_task

        # Send message
        await self._send_message(json.dumps(message))

        try:
            # Wait for response
            return await future
        finally:
            # Cancel timeout task if it's still running
            if message_id in self._timeout_tasks:
                timeout_task = self._timeout_tasks.pop(message_id)
                if not timeout_task.done():
                    timeout_task.cancel()

    async def wait_for_next_future_websocket_event(
        self,
        event_type: str,
        timeout: float = 30.0
    ) -> Dict[str, Union[str, int, float, bool, None, Dict, list]]:
        """Wait for a specific event type to arrive.

        Args:
            event_type: The event type to wait for
            timeout: Timeout in seconds (default: 30.0)

        Returns:
            Event payload as dict

        Raises:
            asyncio.TimeoutError: If timeout is reached
        """
        # Cancel existing waiter for same event type
        if event_type in self.event_waiters:
            existing = self.event_waiters[event_type]
            if existing.timeout_handle:
                existing.timeout_handle.cancel()
            if not existing.future.done():
                existing.future.set_exception(Exception("Replaced by new wait"))

        # Create new waiter
        future: asyncio.Future[Dict[str, Union[str, int, float, bool, None, Dict, list]]] = asyncio.Future()

        async def timeout_handler() -> None:
            await asyncio.sleep(timeout)
            if event_type in self.event_waiters:
                del self.event_waiters[event_type]
                if not future.done():
                    future.set_exception(
                        asyncio.TimeoutError(f"Timeout waiting for event: {event_type}")
                    )

        timeout_task = asyncio.create_task(timeout_handler())
        self._event_timeout_tasks[event_type] = timeout_task

        self.event_waiters[event_type] = PendingRequest(
            future=future,
            timeout_handle=None
        )

        return await future

    def add_streaming_task_handler(
        self,
        unique_task_id: str,
        handler: StreamingTaskHandler
    ) -> None:
        """Register callbacks for a streaming command's output.

        Args:
            unique_task_id: Unique ID for the running task
            handler: Callback functions for stdout, stderr, and close events
        """
        self.streaming_handlers[unique_task_id] = handler

    async def _send_message(self, message: str) -> None:
        """Send a single message through WebSocket.

        Args:
            message: JSON-encoded message string
        """
        if self.connection_state != "connected" or not self.ws:
            self.message_queue.append(message)
            return

        try:
            await self.ws.send(message)
        except Exception as e:
            print(f"[SandboxWebSocket] Error sending message: {e}")
            self.message_queue.append(message)

    def _flush_message_queue(self) -> None:
        """Flush queued messages after reconnection."""
        if self.message_queue and self.ws and self.connection_state == "connected":
            queue = self.message_queue[:]
            self.message_queue = []

            async def send_queued() -> None:
                for msg in queue:
                    await self._send_message(msg)

            asyncio.create_task(send_queued())

    async def _receive_messages(self) -> None:
        """Continuously receive and process messages."""
        try:
            while self.ws and self.connection_state == "connected":
                try:
                    raw_data = await self.ws.recv()
                    message = json.loads(raw_data)
                    await self._handle_message(message)
                except websockets.exceptions.ConnectionClosed:
                    break
                except Exception as e:
                    print(f"[SandboxWebSocket] Error receiving message: {e}")
        finally:
            await self._on_close()

    async def _handle_message(self, message: Dict[str, Union[str, int, float, bool, None, Dict, list]]) -> None:
        """Handle incoming WebSocket message.

        Args:
            message: Parsed message dict
        """
        message_id = message.get("messageId")
        payload = message.get("payload", {})
        if not isinstance(payload, dict):
            return
        
        event_type = payload.get("eventType")
        if not isinstance(event_type, str):
            return
        

        # Handle streaming task events
        if event_type == "StreamLongRunningTaskEvent":
            await self._handle_streaming_event(payload)
            return

        # Handle request-response - check messageId first
        if message_id and isinstance(message_id, str):
            if message_id in self.pending_requests:
                pending = self.pending_requests.pop(message_id)
                # Cancel timeout task if it exists
                if message_id in self._timeout_tasks:
                    timeout_task = self._timeout_tasks.pop(message_id)
                    if not timeout_task.done():
                        timeout_task.cancel()
                if not pending.future.done():
                    pending.future.set_result(payload)
                return

        # Handle event waiters (for events without messageId)
        if event_type and event_type in self.event_waiters:
            waiter = self.event_waiters.pop(event_type)
            # Cancel timeout task if it exists
            if event_type in self._event_timeout_tasks:
                timeout_task = self._event_timeout_tasks.pop(event_type)
                if not timeout_task.done():
                    timeout_task.cancel()
            if not waiter.future.done():
                waiter.future.set_result(payload)

    async def _handle_streaming_event(self, payload: Dict[str, Union[str, int, float, bool, None, Dict, list]]) -> None:
        """Handle streaming task event.

        Args:
            payload: Event payload
        """
        unique_task_id = payload.get("uniqueTaskId")
        event_details = payload.get("eventDetails", {})

        if not isinstance(unique_task_id, str) or unique_task_id not in self.streaming_handlers:
            return

        if not isinstance(event_details, dict):
            return

        handler = self.streaming_handlers[unique_task_id]
        event_type = event_details.get("type")

        if event_type == "io":
            if "stdout" in event_details and handler.on_stdout:
                stdout_val = event_details.get("stdout")
                if isinstance(stdout_val, str):
                    handler.on_stdout(stdout_val)
            if "stderr" in event_details and handler.on_stderr:
                stderr_val = event_details.get("stderr")
                if isinstance(stderr_val, str):
                    handler.on_stderr(stderr_val)
        elif event_type == "close":
            if handler.on_close:
                code_val = event_details.get("code", 0)
                exit_code = code_val if isinstance(code_val, int) else 0
                handler.on_close(exit_code)
            # Clean up handler
            del self.streaming_handlers[unique_task_id]

    def _start_health_ping(self) -> None:
        """Start health ping task."""
        if self.health_ping_task:
            self.health_ping_task.cancel()

        async def ping_loop() -> None:
            await asyncio.sleep(5)
            while self.connection_state == "connected":
                try:
                    ping_request = HealthPingRequest(event_type="HealthPing")
                    await self.send(ping_request.model_dump(by_alias=True), timeout=5.0)
                    await asyncio.sleep(10)
                except Exception as e:
                    print(f"[SandboxWebSocket] Health ping failed: {e}")
                    break

        self.health_ping_task = asyncio.create_task(ping_loop())

    async def _on_close(self) -> None:
        """Handle WebSocket closure."""
        self.connection_state = "disconnected"
        await self._cleanup()

        # Auto-reconnect if enabled
        if self.should_auto_reconnect:
            await asyncio.sleep(2)
            try:
                await self.connect()
            except Exception as e:
                print(f"[SandboxWebSocket] Reconnect failed: {e}")

    async def _cleanup(self) -> None:
        """Clean up resources."""
        # Cancel tasks
        if self.health_ping_task:
            self.health_ping_task.cancel()
            self.health_ping_task = None

        if self.receive_task:
            self.receive_task.cancel()
            self.receive_task = None

        # Close WebSocket
        if self.ws:
            try:
                await self.ws.close()
            except Exception:
                pass
            self.ws = None

        # Reject pending requests
        for timeout_task in self._timeout_tasks.values():
            if not timeout_task.done():
                timeout_task.cancel()
        self._timeout_tasks.clear()
        
        for pending in self.pending_requests.values():
            if not pending.future.done():
                pending.future.set_exception(Exception("WebSocket closed"))
        self.pending_requests.clear()

        # Reject event waiters
        for timeout_task in self._event_timeout_tasks.values():
            if not timeout_task.done():
                timeout_task.cancel()
        self._event_timeout_tasks.clear()
        
        for waiter in self.event_waiters.values():
            if not waiter.future.done():
                waiter.future.set_exception(Exception("WebSocket closed"))
        self.event_waiters.clear()

        # Clear message queue
        self.message_queue = []

    @staticmethod
    def _generate_message_id() -> str:
        """Generate a unique message ID.

        Returns:
            Random message ID string
        """
        return secrets.token_urlsafe(16)
