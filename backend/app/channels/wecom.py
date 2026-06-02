from __future__ import annotations

import asyncio
import base64
import hashlib
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, cast

from app.channels.base import Channel
from app.channels.message_bus import (
    InboundMessageType,
    MessageBus,
    OutboundMessage,
    ResolvedAttachment,
)

logger = logging.getLogger(__name__)

_WECOM_FILE_METADATA_KEYS = ("filename", "file_name", "name", "title", "content_type", "mime_type", "mimetype", "mime")
_WECOM_FILE_URL_KEYS = ("url", "download_url", "downloadUrl", "media_url", "mediaUrl", "voice_url", "voiceUrl", "video_url", "videoUrl")
_WECOM_FILE_AESKEY_KEYS = ("aeskey", "aes_key", "aesKey")
_WECOM_FILE_MSG_TYPES = {"image", "file", "voice", "audio", "video"}
_WECOM_SPECIFIC_EVENT_MSG_TYPES = {"text", "image", "mixed", "voice", "file"}


@dataclass
class WeComInbound:
    text: str
    files: list[dict[str, Any]]


def _extract_wecom_file_metadata(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value.strip()
        for key in _WECOM_FILE_METADATA_KEYS
        if isinstance((value := payload.get(key)), str) and value.strip()
    }


def _first_wecom_text_value(payload: dict[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _wecom_file_from_payload(item_type: str, payload: dict[str, Any]) -> dict[str, Any] | None:
    url = _first_wecom_text_value(payload, _WECOM_FILE_URL_KEYS)
    aeskey = _first_wecom_text_value(payload, _WECOM_FILE_AESKEY_KEYS)
    if not url:
        return None
    return {
        "type": item_type,
        "url": url,
        "aeskey": aeskey or None,
        **_extract_wecom_file_metadata(payload),
    }


def _wecom_media_placeholder(item_type: str) -> str:
    if item_type in {"voice", "audio"}:
        return "（receive voice）"
    if item_type == "video":
        return "（receive video）"
    return "（receive image/file）"


def _wecom_media_text(item_type: str, payload: dict[str, Any]) -> str:
    content = _first_wecom_text_value(payload, ("content", "text", "recognition"))
    if not content:
        return ""
    if item_type in {"voice", "audio"}:
        return f"Voice message: {content}"
    return content


def _extract_wecom_mixed_items(items: Any) -> tuple[list[str], list[dict[str, Any]]]:
    if not isinstance(items, list):
        return [], []

    parts: list[str] = []
    files: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        item_type = item.get("msgtype")
        if item_type == "text":
            content = (((item or {}).get("text") or {}).get("content") or "").strip()
            if content:
                parts.append(content)
        elif item_type in _WECOM_FILE_MSG_TYPES:
            payload = item.get(item_type) or {}
            media_text = _wecom_media_text(item_type, payload) if isinstance(payload, dict) else ""
            if media_text:
                parts.append(media_text)
            if isinstance(payload, dict) and (file_info := _wecom_file_from_payload(item_type, payload)):
                files.append(file_info)
            elif item_type in {"voice", "audio", "video"} and not media_text:
                parts.append(_wecom_media_placeholder(item_type))
    return parts, files


def _extract_wecom_body_content(
    body: dict[str, Any],
    *,
    include_file_placeholder: bool = True,
) -> tuple[list[str], list[dict[str, Any]]]:
    msgtype = body.get("msgtype")
    parts: list[str] = []
    files: list[dict[str, Any]] = []

    text = ((body.get("text") or {}).get("content") or "").strip()
    if text:
        parts.append(text)

    for item_type in _WECOM_FILE_MSG_TYPES:
        payload = body.get(item_type) or {}
        media_text = _wecom_media_text(item_type, payload) if isinstance(payload, dict) else ""
        if media_text:
            parts.append(media_text)
        if isinstance(payload, dict) and (file_info := _wecom_file_from_payload(item_type, payload)):
            files.append(file_info)
        elif msgtype == item_type and item_type in {"voice", "audio", "video"} and not media_text:
            parts.append(_wecom_media_placeholder(item_type))

    mixed = body.get("mixed") or {}
    mixed_parts, mixed_files = _extract_wecom_mixed_items(mixed.get("msg_item") if isinstance(mixed, dict) else None)
    parts.extend(mixed_parts)
    files.extend(mixed_files)

    if include_file_placeholder and msgtype in _WECOM_FILE_MSG_TYPES and not parts and files:
        parts.append(_wecom_media_placeholder(msgtype))
    return parts, files


def _extract_wecom_quote_content(body: dict[str, Any]) -> tuple[list[str], list[dict[str, Any]]]:
    quote_obj = body.get("quote") or {}
    if not isinstance(quote_obj, dict):
        return [], []

    quote_parts, quote_files = _extract_wecom_body_content(quote_obj, include_file_placeholder=False)
    parts = [f"Quote message: {part}" for part in quote_parts]
    if quote_files:
        parts.append("Quote file: see uploaded file attachment.")
    return parts, quote_files


def _parse_wecom_inbound(frame: dict[str, Any]) -> WeComInbound | None:
    body = frame.get("body", {}) or {}
    if not isinstance(body, dict):
        return None

    parts, files = _extract_wecom_body_content(body)
    quote_parts, quote_files = _extract_wecom_quote_content(body)
    parts.extend(quote_parts)
    files.extend(quote_files)

    text = "\n".join(part for part in parts if part).strip()
    if not text and files:
        text = "（receive image/file）"
    if not text and not files:
        return None
    return WeComInbound(text=text, files=files)


class WeComChannel(Channel):
    def __init__(self, bus: MessageBus, config: dict[str, Any]) -> None:
        channel_name = config.get("channel_name")
        super().__init__(
            name=channel_name if isinstance(channel_name, str) and channel_name else "wecom",
            bus=bus,
            config=config,
        )
        self._bot_id: str | None = None
        self._bot_secret: str | None = None
        self._ws_client = None
        self._ws_task: asyncio.Task | None = None
        self._ws_frames: dict[str, dict[str, Any]] = {}
        self._ws_stream_ids: dict[str, str] = {}
        self._working_message = "Working on it..."
        self._ws_reconnect_initial_delay = 1.0
        self._ws_reconnect_max_delay = 30.0

    @property
    def supports_streaming(self) -> bool:
        return True

    def _clear_ws_context(self, thread_ts: str | None) -> None:
        if not thread_ts:
            return
        self._ws_frames.pop(thread_ts, None)
        self._ws_stream_ids.pop(thread_ts, None)

    def _create_ws_client(self):
        if not self._bot_id or not self._bot_secret:
            raise RuntimeError("WeCom channel requires bot_id and bot_secret")
        from aibot import WSClient, WSClientOptions

        ws_client = WSClient(WSClientOptions(bot_id=self._bot_id, secret=self._bot_secret, logger=logger))
        ws_client.on("message", self._on_ws_message)
        ws_client.on("message.text", self._on_ws_text)
        ws_client.on("message.mixed", self._on_ws_mixed)
        ws_client.on("message.image", self._on_ws_image)
        ws_client.on("message.file", self._on_ws_file)
        ws_client.on("message.voice", self._on_ws_voice)
        ws_client.on("message.video", self._on_ws_video)
        ws_client.on("error", self._on_ws_error)
        return ws_client

    def _on_ws_error(self, error: Exception) -> None:
        logger.warning("[WeCom] WebSocket SDK error: %s", error)

    def _disconnect_ws_client(self) -> None:
        if not self._ws_client:
            return
        try:
            self._ws_client.disconnect()
        except Exception:
            logger.debug("[WeCom] error while disconnecting WebSocket client", exc_info=True)
        finally:
            self._ws_client = None

    async def _run_ws_forever(self) -> None:
        reconnect_attempt = 0
        while self._running:
            should_reconnect = False
            try:
                self._ws_client = self._create_ws_client()
                logger.info("[WeCom] starting WebSocket connection supervisor")
                await self._ws_client.connect()
                reconnect_attempt = 0
                while self._running:
                    await asyncio.sleep(3600)
            except asyncio.CancelledError:
                logger.info("[WeCom] WebSocket supervisor cancelled")
                raise
            except Exception as exc:
                should_reconnect = self._running
                if self._running:
                    logger.exception("[WeCom] WebSocket connection failed or exited unexpectedly: %s", exc)
            finally:
                self._disconnect_ws_client()

            if not self._running or not should_reconnect:
                break

            delay = min(self._ws_reconnect_max_delay, self._ws_reconnect_initial_delay * (2**reconnect_attempt))
            reconnect_attempt += 1
            logger.info("[WeCom] reconnecting WebSocket in %.1fs (attempt %d)", delay, reconnect_attempt)
            try:
                await asyncio.sleep(delay)
            except asyncio.CancelledError:
                logger.info("[WeCom] WebSocket supervisor cancelled during reconnect backoff")
                raise

    async def _send_ws_upload_command(self, req_id: str, body: dict[str, Any], cmd: str) -> dict[str, Any]:
        if not self._ws_client:
            raise RuntimeError("WeCom WebSocket client is not available")

        ws_manager = getattr(self._ws_client, "_ws_manager", None)
        send_reply = getattr(ws_manager, "send_reply", None)
        if not callable(send_reply):
            raise RuntimeError("Installed wecom-aibot-python-sdk does not expose the WebSocket media upload API expected by DeerFlow. Use wecom-aibot-python-sdk==0.1.6 or update the adapter.")

        send_reply_async = cast(Callable[[str, dict[str, Any], str], Awaitable[dict[str, Any]]], send_reply)
        return await send_reply_async(req_id, body, cmd)

    async def start(self) -> None:
        if self._running:
            return

        bot_id = self.config.get("bot_id")
        bot_secret = self.config.get("bot_secret")
        working_message = self.config.get("working_message")

        self._bot_id = bot_id if isinstance(bot_id, str) and bot_id else None
        self._bot_secret = bot_secret if isinstance(bot_secret, str) and bot_secret else None
        self._working_message = working_message if isinstance(working_message, str) and working_message else "Working on it..."

        if not self._bot_id or not self._bot_secret:
            logger.error("WeCom channel requires bot_id and bot_secret")
            return

        try:
            import aibot  # noqa: F401
        except ImportError:
            logger.error("wecom-aibot-python-sdk is not installed. Install it with: uv add wecom-aibot-python-sdk")
            return

        self._running = True
        self.bus.subscribe_outbound(self._on_outbound)
        self._ws_task = asyncio.create_task(self._run_ws_forever())
        logger.info("WeCom channel started")

    async def stop(self) -> None:
        self._running = False
        self.bus.unsubscribe_outbound(self._on_outbound)
        task = self._ws_task
        self._ws_task = None
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            except Exception:
                logger.debug("[WeCom] WebSocket supervisor exited during stop", exc_info=True)
        self._disconnect_ws_client()
        self._ws_frames.clear()
        self._ws_stream_ids.clear()
        logger.info("WeCom channel stopped")

    async def send(self, msg: OutboundMessage, *, _max_retries: int = 3) -> None:
        if self._ws_client:
            await self._send_ws(msg, _max_retries=_max_retries)
            return
        logger.warning("[WeCom] send called but WebSocket client is not available")

    async def _on_outbound(self, msg: OutboundMessage) -> None:
        if msg.channel_name != self.name:
            return

        try:
            await self.send(msg)
        except Exception:
            logger.exception("Failed to send outbound message on channel %s", self.name)
            if msg.is_final:
                self._clear_ws_context(msg.thread_ts)
            return

        for attachment in msg.attachments:
            try:
                success = await self.send_file(msg, attachment)
                if not success:
                    logger.warning("[%s] file upload skipped for %s", self.name, attachment.filename)
            except Exception:
                logger.exception("[%s] failed to upload file %s", self.name, attachment.filename)

        if msg.is_final:
            self._clear_ws_context(msg.thread_ts)

    async def send_file(self, msg: OutboundMessage, attachment: ResolvedAttachment) -> bool:
        if not msg.is_final:
            return True
        if not self._ws_client:
            return False
        if not msg.thread_ts:
            return False
        frame = self._ws_frames.get(msg.thread_ts)
        if not frame:
            return False

        media_type = "image" if attachment.is_image else "file"
        size_limit = 2 * 1024 * 1024 if attachment.is_image else 20 * 1024 * 1024
        if attachment.size > size_limit:
            logger.warning(
                "[WeCom] %s too large (%d bytes), skipping: %s",
                media_type,
                attachment.size,
                attachment.filename,
            )
            return False

        try:
            media_id = await self._upload_media_ws(
                media_type=media_type,
                filename=attachment.filename,
                path=str(attachment.actual_path),
                size=attachment.size,
            )
            if not media_id:
                return False

            body = {media_type: {"media_id": media_id}, "msgtype": media_type}
            await self._ws_client.reply(frame, body)
            logger.debug("[WeCom] %s sent via ws: %s", media_type, attachment.filename)
            return True
        except Exception:
            logger.exception("[WeCom] failed to upload/send file via ws: %s", attachment.filename)
            return False

    async def _on_ws_message(self, frame: dict[str, Any]) -> None:
        body = frame.get("body", {}) or {}
        msgtype = body.get("msgtype") if isinstance(body, dict) else None
        if msgtype in _WECOM_SPECIFIC_EVENT_MSG_TYPES:
            return
        await self._publish_parsed_ws_inbound(frame)

    async def _on_ws_text(self, frame: dict[str, Any]) -> None:
        await self._publish_parsed_ws_inbound(frame)

    async def _on_ws_mixed(self, frame: dict[str, Any]) -> None:
        await self._publish_parsed_ws_inbound(frame)

    async def _on_ws_image(self, frame: dict[str, Any]) -> None:
        await self._publish_parsed_ws_inbound(frame)

    async def _on_ws_file(self, frame: dict[str, Any]) -> None:
        await self._publish_parsed_ws_inbound(frame)

    async def _on_ws_voice(self, frame: dict[str, Any]) -> None:
        await self._publish_parsed_ws_inbound(frame)

    async def _on_ws_video(self, frame: dict[str, Any]) -> None:
        await self._publish_parsed_ws_inbound(frame)

    async def _publish_parsed_ws_inbound(self, frame: dict[str, Any]) -> None:
        body = frame.get("body", {}) or {}
        msgtype = body.get("msgtype") if isinstance(body, dict) else None
        if msgtype in {"voice", "audio", "video"}:
            payload = body.get(msgtype) if isinstance(body, dict) else None
            logger.info(
                "[WeCom] inbound %s keys: %s",
                msgtype,
                sorted(payload.keys()) if isinstance(payload, dict) else [],
            )
        inbound = _parse_wecom_inbound(frame)
        if not inbound:
            logger.info("[WeCom] ignored inbound msgtype=%s: no text/files", msgtype)
            return
        await self._publish_ws_inbound(frame, inbound.text, files=inbound.files)

    async def _publish_ws_inbound(
        self,
        frame: dict[str, Any],
        text: str,
        *,
        files: list[dict[str, Any]] | None = None,
    ) -> None:
        if not self._ws_client:
            return
        try:
            from aibot import generate_req_id
        except Exception:
            return

        body = frame.get("body", {}) or {}
        msg_id = body.get("msgid")
        if not msg_id:
            return

        user_id = (body.get("from") or {}).get("userid")

        inbound_type = InboundMessageType.COMMAND if text.startswith("/") else InboundMessageType.CHAT
        inbound = self._make_inbound(
            chat_id=user_id,  # keep user's conversation in memory
            user_id=user_id,
            text=text,
            msg_type=inbound_type,
            thread_ts=msg_id,
            files=files or [],
            metadata={"aibotid": body.get("aibotid"), "chattype": body.get("chattype")},
        )
        inbound.topic_id = user_id  # keep the same thread

        stream_id = generate_req_id("stream")
        self._ws_frames[msg_id] = frame
        self._ws_stream_ids[msg_id] = stream_id

        try:
            await self._ws_client.reply_stream(frame, stream_id, self._working_message, False)
        except Exception:
            pass

        await self.bus.publish_inbound(inbound)

    async def _send_ws(self, msg: OutboundMessage, *, _max_retries: int = 3) -> None:
        if not self._ws_client:
            return
        try:
            from aibot import generate_req_id
        except Exception:
            generate_req_id = None

        if msg.thread_ts and msg.thread_ts in self._ws_frames:
            frame = self._ws_frames[msg.thread_ts]
            stream_id = self._ws_stream_ids.get(msg.thread_ts)
            if not stream_id and generate_req_id:
                stream_id = generate_req_id("stream")
                self._ws_stream_ids[msg.thread_ts] = stream_id
            if not stream_id:
                return

            last_exc: Exception | None = None
            for attempt in range(_max_retries):
                try:
                    await self._ws_client.reply_stream(frame, stream_id, msg.text, bool(msg.is_final))
                    return
                except Exception as exc:
                    last_exc = exc
                    if attempt < _max_retries - 1:
                        await asyncio.sleep(2**attempt)
            if last_exc:
                raise last_exc

        body = {"msgtype": "markdown", "markdown": {"content": msg.text}}
        last_exc = None
        for attempt in range(_max_retries):
            try:
                await self._ws_client.send_message(msg.chat_id, body)
                return
            except Exception as exc:
                last_exc = exc
                if attempt < _max_retries - 1:
                    await asyncio.sleep(2**attempt)
        if last_exc:
            raise last_exc

    async def _upload_media_ws(
        self,
        *,
        media_type: str,
        filename: str,
        path: str,
        size: int,
    ) -> str | None:
        if not self._ws_client:
            return None
        try:
            from aibot import generate_req_id
        except Exception:
            return None

        chunk_size = 512 * 1024
        total_chunks = (size + chunk_size - 1) // chunk_size
        if total_chunks < 1 or total_chunks > 100:
            logger.warning("[WeCom] invalid total_chunks=%d for %s", total_chunks, filename)
            return None

        md5_hasher = hashlib.md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                md5_hasher.update(chunk)
        md5 = md5_hasher.hexdigest()

        init_req_id = generate_req_id("aibot_upload_media_init")
        init_body = {
            "type": media_type,
            "filename": filename,
            "total_size": int(size),
            "total_chunks": int(total_chunks),
            "md5": md5,
        }
        init_ack = await self._send_ws_upload_command(init_req_id, init_body, "aibot_upload_media_init")
        upload_id = (init_ack.get("body") or {}).get("upload_id")
        if not upload_id:
            logger.warning("[WeCom] upload init returned no upload_id: %s", init_ack)
            return None

        with open(path, "rb") as f:
            for idx in range(total_chunks):
                data = f.read(chunk_size)
                if not data:
                    break
                chunk_req_id = generate_req_id("aibot_upload_media_chunk")
                chunk_body = {
                    "upload_id": upload_id,
                    "chunk_index": int(idx),
                    "base64_data": base64.b64encode(data).decode("utf-8"),
                }
                await self._send_ws_upload_command(chunk_req_id, chunk_body, "aibot_upload_media_chunk")

        finish_req_id = generate_req_id("aibot_upload_media_finish")
        finish_ack = await self._send_ws_upload_command(finish_req_id, {"upload_id": upload_id}, "aibot_upload_media_finish")
        media_id = (finish_ack.get("body") or {}).get("media_id")
        if not media_id:
            logger.warning("[WeCom] upload finish returned no media_id: %s", finish_ack)
            return None
        return media_id
