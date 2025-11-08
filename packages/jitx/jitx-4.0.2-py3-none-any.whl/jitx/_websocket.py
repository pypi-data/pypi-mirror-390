"""WebSocket communication utilities.

This module provides utilities for communicating with the JITX backend
via WebSocket connections, including message handling and conversation management.
"""

import json
import logging
import os
from collections.abc import Awaitable, Callable
from typing import Any, overload

import websockets

logger = logging.getLogger("jitx.websocket")


# Generate unique conversation IDs.
cid_counter = 0


def new_cid(prefix: str):
    """Generate a new conversation ID.

    Args:
        prefix: Prefix for the conversation ID.

    Returns:
        Unique conversation ID string.
    """
    global cid_counter
    cid_counter += 1
    return f"{prefix}-{cid_counter}"


def get_websocket_uri() -> str:
    """Get the configured WebSocket URI.

    Returns:
        The WebSocket URI string.

    Raises:
        RuntimeError: If the WebSocket URI has not been configured.
    """
    logger.debug(f"Getting websocket URI: {os.environ.get('JITX_WEBSOCKET_URI')}")
    uri = os.environ.get("JITX_WEBSOCKET_URI")
    if uri is None:
        uri = set_websocket_uri()
    if uri is None:
        raise RuntimeError("WebSocket URI not set. Call set_websocket_uri() first.")
    return uri


def _find_socket_file() -> str:
    import os

    path = os.getcwd()
    while path:
        file = os.path.join(path, ".socket.jitx")
        if os.path.exists(file):
            return file
        rem = os.path.dirname(path)
        if rem == path:
            break
        path = rem
    raise Exception("Unable to determine socket URI, please specify --port")


@overload
def set_websocket_uri(*, host: str, port: int) -> None: ...
@overload
def set_websocket_uri(*, uri: str) -> None: ...
@overload
def set_websocket_uri(*, file: str) -> None: ...
@overload
def set_websocket_uri() -> None: ...


def set_websocket_uri(
    *,
    host: str | None = None,
    port: int | None = None,
    uri: str | None = None,
    file: str | None = None,
):
    """Set the WebSocket URI for backend communication.

    Args:
        host: WebSocket server hostname.
        port: WebSocket server port.
    """
    if file is not None:
        with open(file) as f:
            try:
                ob = json.load(f)
                uri = ob["uri"]
            except Exception:
                raise Exception(
                    f"Invalid .socket.jitx file {file}, unable to determine socket URI"
                ) from None
            if not isinstance(uri, str):
                raise Exception(
                    "Invalid .socket.jitx file {file}, unable to determine socket URI"
                )
    elif uri is None:
        if host is not None and port is not None:
            uri = f"ws://{host}:{port}"
        else:
            # all none, look for file.
            return set_websocket_uri(file=_find_socket_file())

    logger.debug(f"Setting websocket URI to {uri}")
    os.environ["JITX_WEBSOCKET_URI"] = uri
    return uri


FLAG_CONTINUE = 1


async def on_websocket_message(
    type: str,
    body: dict[str, Any],
    on_response_in_progress: Callable[
        [dict[str, Any], Callable[[str, dict[str, Any]], Awaitable[None]]],
        Awaitable[None],
    ],
    on_error: Callable[[dict[str, Any]], Any],
    on_success: Callable[[dict[str, Any]], Any],
    on_connection_closed: Callable[[Exception], Any],
    cid_prefix: str,
):
    """Handle WebSocket message communication.

    Args:
        type: Message type to send.
        body: Message body data.
        on_response_in_progress: Callback for handling responses in progress.
        on_error: Callback for handling error responses.
        on_success: Callback for handling successful responses.
        on_connection_closed: Callback for handling connection closure.
        cid_prefix: Prefix for the conversation ID.
    """
    uri = get_websocket_uri()
    cid = new_cid(cid_prefix)

    # Setting max_size of reply to 1GB, needed by parts DB.
    async with websockets.connect(uri, max_size=1_000_000_000) as websocket:
        await send_message(websocket, cid, type, body)

        # Wait for replies until we get a message with flg != FLAG_CONTINUE
        while True:
            try:
                # Wait for reply
                response = await websocket.recv()
                message = json.loads(response)

                # Ignore messages from other conversations
                if message.get("cid") != cid:
                    continue

                # Handle reponses in progress.
                if message.get("flg") & FLAG_CONTINUE:

                    async def send_msg(type, body):
                        await send_message(websocket, cid, type, body)

                    await on_response_in_progress(message, send_msg)
                    continue

                # Handle the terminal message.
                match message.get("type"):
                    case "ok":
                        return on_success(message["body"])
                    case "error":
                        return on_error(message["body"])
                    case _:
                        raise RuntimeError(
                            f"Unhandled terminal message type: {message}"
                        )

            except websockets.exceptions.ConnectionClosed as e:
                return on_connection_closed(e)


async def send_message(
    websocket: websockets.ClientConnection, cid: str, type: str, body: dict[str, Any]
) -> None:
    """Send a message to the WebSocket server.

    Args:
        websocket: The WebSocket connection
        type: The message type
        body: The message body

    Raises:
        ConnectionClosed: When the connection is closed.
    """
    payload = {
        "own": True,
        "ns": "des",
        "cid": cid,
        "flg": 0,
        "type": type,
        "body": body,
    }
    data = json.dumps(payload)
    return await websocket.send(data)
