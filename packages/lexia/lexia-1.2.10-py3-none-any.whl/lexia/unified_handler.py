"""
Unified Lexia Handler
=====================

Single, clean interface for all Lexia platform communication.
Supports both production (Centrifugo) and dev mode (in-memory streaming).
"""

import logging
import threading
import os
import traceback
from typing import Any, Dict, List, Optional, Sequence
from urllib.parse import urlparse
from .centrifugo_client import CentrifugoClient
from .dev_stream_client import DevStreamClient
from .api_client import APIClient
from .response_handler import create_complete_response

logger = logging.getLogger(__name__)


def _normalize_button_args(button_defs: Sequence[Dict[str, Any]]) -> Sequence[Dict[str, Any]]:
    if len(button_defs) == 1 and isinstance(button_defs[0], (list, tuple)):
        return button_defs[0]
    return button_defs


def _build_button(
    kind: str,
    label: Optional[str],
    row: Optional[int],
    color: Optional[str],
    *,
    url: Optional[str] = None,
    action_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    kind = (kind or "").strip().lower()
    if kind not in ("link", "action"):
        logger.warning("Unsupported button kind '%s'", kind)
        return None

    label_text = (label or "").strip()
    if not label_text:
        logger.warning("Button missing required 'label'")
        return None

    resolved_row = row if isinstance(row, int) and row > 0 else 1

    button: Dict[str, Any] = {
        "type": kind,
        "label": label_text,
        "row": resolved_row,
    }

    if color:
        color_text = str(color).strip()
        if color_text:
            button["color"] = color_text

    if kind == "link":
        url_text = (url or "").strip() if isinstance(url, str) else ""
        if not url_text:
            logger.warning("Link button '%s' missing required URL", label_text)
            return None
        button["url"] = url_text
    else:
        action_text = (action_id or "").strip() if isinstance(action_id, str) else ""
        if not action_text:
            logger.warning("Action button '%s' missing required ID", label_text)
            return None
        button["id"] = action_text

    return button


def _render_button_block(buttons: Sequence[Dict[str, Any]]) -> str:
    preferred_order = ["label", "id", "url", "color", "row", "tooltip", "description", "icon"]
    block_lines: List[str] = ["[lexia.buttons.start]"]

    for idx, button in enumerate(buttons):
        entry_lines = [f"- type: {button['type']}"]
        entry_lines.append(f"  label: {button['label']}")

        for field in preferred_order:
            if field == "label":
                continue
            if field in button and button[field] is not None:
                entry_lines.append(f"  {field}: {button[field]}")

        for key, value in button.items():
            if key in ("type", "label") or key in preferred_order:
                continue
            if value is None:
                continue
            entry_lines.append(f"  {key}: {value}")

        block_lines.extend(entry_lines)
        if idx != len(buttons) - 1:
            block_lines.append("")

    block_lines.append("[lexia.buttons.end]")
    payload = "\n".join(block_lines)
    if not payload.endswith("\n"):
        payload += "\n"
    return payload


def create_link_button_block(label: str, url: str, row: int = 1, color: Optional[str] = None) -> str:
    """
    Create a markdown block representing a single link button.

    Returns the `[lexia.buttons.start]` block so callers can stream or reuse it.
    """
    button = _build_button("link", label, row, color, url=url)
    if not button:
        raise ValueError("Invalid link button definition")
    return _render_button_block([button])


def create_action_button_block(label: str, action_id: str, row: int = 1, color: Optional[str] = None) -> str:
    """
    Create a markdown block representing a single action button.

    Returns the `[lexia.buttons.start]` block so callers can stream or reuse it.
    """
    button = _build_button("action", label, row, color, action_id=action_id)
    if not button:
        raise ValueError("Invalid action button definition")
    return _render_button_block([button])


class LexiaHandler:
    """Clean, unified interface for all Lexia communication."""
    
    def __init__(self, dev_mode: bool = None):
        """
        Initialize LexiaHandler with optional dev mode.
        
        Args:
            dev_mode: If True, uses DevStreamClient instead of Centrifugo.
                     If None, checks LEXIA_DEV_MODE environment variable.
        """
        # Determine dev mode from parameter or environment
        if dev_mode is None:
            dev_mode = os.environ.get('LEXIA_DEV_MODE', 'false').lower() in ('true', '1', 'yes')
        
        self.dev_mode = dev_mode
        
        # Initialize appropriate streaming client
        if self.dev_mode:
            self.stream_client = DevStreamClient()
            logger.info("🔧 LexiaHandler initialized in DEV MODE (no Centrifugo)")
        else:
            self.stream_client = CentrifugoClient()
            logger.info("🚀 LexiaHandler initialized in PRODUCTION MODE (Centrifugo)")
        
        self.api = APIClient()
        
        # Internal aggregation buffers keyed by response UUID
        self._buffers = {}
        self._buffers_lock = threading.Lock()
        
        # Simple alias map to turn semantic commands into Lexia markers
        self._marker_aliases = {
            # image
            'show image load': "[lexia.loading.image.start]\n\n",
            'end image load': "[lexia.loading.image.end]\n\n",
            'hide image load': "[lexia.loading.image.end]\n\n",
            # code
            'show code load': "[lexia.loading.code.start]\n\n",
            'end code load': "[lexia.loading.code.end]\n\n",
            # search
            'show search load': "[lexia.loading.search.start]\n\n",
            'end search load': "[lexia.loading.search.end]\n\n",
            # thinking
            'show thinking load': "[lexia.loading.thinking.start]\n\n",
            'end thinking load': "[lexia.loading.thinking.end]\n\n",
        }

    def _get_loading_marker(self, kind: str, action: str) -> str:
        """Return a standardized loading marker string for a given kind/action."""
        kind_norm = (kind or '').strip().lower()
        if kind_norm not in ("image", "code", "search", "thinking"):
            kind_norm = "thinking"
        action_norm = "start" if action == "start" else "end"
        return f"[lexia.loading.{kind_norm}.{action_norm}]\n\n"

    # Per-response session object to avoid passing data repeatedly
    class _Session:
        def __init__(self, handler: 'LexiaHandler', data):
            self._handler = handler
            # Keep original request object to preserve headers/urls/ids
            self._data = data
            # Progressive tracing buffer
            self._progressive_trace_buffer = None
            self._progressive_trace_visibility = "all"
            # Button helper (preferred API)
            self.button = LexiaHandler._ButtonHelper(self)
            # Optionally preconfigure centrifugo (prod only)
            if (not handler.dev_mode and 
                hasattr(data, 'stream_url') and hasattr(data, 'stream_token')):
                handler.update_centrifugo_config(data.stream_url, data.stream_token)

        def stream(self, content: str) -> None:
            self._handler.stream(self._data, content)

        def close(self, usage_info=None, file_url=None) -> str:
            return self._handler.close(self._data, usage_info=usage_info, file_url=file_url)

        def error(self, error_message: str, exception: Exception = None, trace: str = None) -> None:
            self._handler.send_error(self._data, error_message, trace=trace, exception=exception)

        # Developer-friendly loading helpers
        def start_loading(self, kind: str = "thinking") -> None:
            marker = self._handler._get_loading_marker(kind, "start")
            self._handler.stream(self._data, marker)

        def end_loading(self, kind: str = "thinking") -> None:
            marker = self._handler._get_loading_marker(kind, "end")
            self._handler.stream(self._data, marker)

        # Image helper: wrap URL with lexia image markers
        def image(self, url: str) -> None:
            if not url:
                return
            payload = f"[lexia.image.start]{url}[lexia.image.end]"
            self._handler.stream(self._data, payload)

        def button_link(self, label: str, url: str, row: int = 1, color: Optional[str] = None) -> None:
            """Deprecated alias for session.button.link()."""
            self.button.link(label, url, row=row, color=color)

        def button_action(self, label: str, action_id: str, row: int = 1, color: Optional[str] = None) -> None:
            """Deprecated alias for session.button.action()."""
            self.button.action(label, action_id, row=row, color=color)

        def buttons_begin(self, default_row: int = 1, default_color: Optional[str] = None) -> None:
            """Deprecated alias for session.button.begin()."""
            self.button.begin(default_row=default_row, default_color=default_color)

        def buttons_add_link(self, label: str, url: str, row: Optional[int] = None, color: Optional[str] = None) -> None:
            """Deprecated alias for session.button.add_link()."""
            self.button.add_link(label, url, row=row, color=color)

        def buttons_add_action(self, label: str, action_id: str, row: Optional[int] = None, color: Optional[str] = None) -> None:
            """Deprecated alias for session.button.add_action()."""
            self.button.add_action(label, action_id, row=row, color=color)

        def buttons_add_link_button(self, *args, **kwargs) -> None:
            """Deprecated alias for session.button.add_link()."""
            self.button.add_link(*args, **kwargs)

        def buttons_add_action_button(self, *args, **kwargs) -> None:
            """Deprecated alias for session.button.add_action()."""
            self.button.add_action(*args, **kwargs)

        def buttons_end(self) -> None:
            """Deprecated alias for session.button.end()."""
            self.button.end()

        def buttons(self, *button_defs: Dict[str, Any], defaults: Optional[Dict[str, Any]] = None) -> None:
            """
            Backwards-compatible helper for dictionary-based button definitions.
            Prefer button_link/button_action going forward.
            """
            if not button_defs:
                logger.warning("buttons() called with no button definitions")
                return

            button_iterable = _normalize_button_args(button_defs)
            default_row = (defaults or {}).get("row", 1)
            default_color = (defaults or {}).get("color")
            collected: List[Dict[str, Any]] = []

            for idx, raw_button in enumerate(button_iterable, start=1):
                if not isinstance(raw_button, dict):
                    logger.warning("Button %s is not a dictionary: %r", idx, raw_button)
                    continue

                kind = raw_button.get("type") or raw_button.get("button_type")
                if not kind:
                    if "url" in raw_button:
                        kind = "link"
                    elif "id" in raw_button:
                        kind = "action"

                label = raw_button.get("label") or raw_button.get("title") or raw_button.get("text")
                row = raw_button.get("row", default_row)
                color = raw_button["color"] if "color" in raw_button else default_color

                if kind == "link":
                    button = _build_button("link", label, row, color, url=raw_button.get("url"))
                elif kind == "action":
                    button = _build_button("action", label, row, color, action_id=raw_button.get("id"))
                else:
                    logger.warning("Button %s missing 'type' and could not infer from contents: %r", idx, raw_button)
                    continue

                if button:
                    # Include any extra keys not covered by helper
                    for key, value in raw_button.items():
                        if key in ("type", "label", "button_type", "title", "text", "id", "url", "row", "color"):
                            continue
                        if value is None:
                            continue
                        button[key] = value
                    collected.append(button)

            if not collected:
                logger.warning("No valid button definitions provided; skipping buttons block.")
                return

            payload = _render_button_block(collected)
            self._handler.stream(self._data, payload)

    class _ButtonHelper:
        """Namespace for button streaming helpers: session.button.*"""

        def __init__(self, session: '_Session'):
            self._session = session
            self._pending: Optional[List[Dict[str, Any]]] = None
            self._defaults: Dict[str, Any] = {"row": 1, "color": None}

        def link(self, label: str, url: str, row: int = 1, color: Optional[str] = None) -> None:
            """Stream a single link button block immediately."""
            button = _build_button("link", label, row, color, url=url)
            if not button:
                return
            payload = _render_button_block([button])
            self._session._handler.stream(self._session._data, payload)

        def action(self, label: str, action_id: str, row: int = 1, color: Optional[str] = None) -> None:
            """Stream a single action button block immediately."""
            button = _build_button("action", label, row, color, action_id=action_id)
            if not button:
                return
            payload = _render_button_block([button])
            self._session._handler.stream(self._session._data, payload)

        def begin(self, default_row: int = 1, default_color: Optional[str] = None) -> None:
            """Start progressive button collection."""
            self._pending = []
            self._defaults = {"row": default_row or 1, "color": default_color}
            logger.debug("Progressive buttons collection started with defaults: %s", self._defaults)

        def add_link(self, label: str, url: str, row: Optional[int] = None, color: Optional[str] = None) -> None:
            """Queue a link button during progressive collection."""
            if self._pending is None:
                logger.warning("session.button.add_link() called without session.button.begin()")
                return
            effective_row = row if row is not None else self._defaults.get("row", 1)
            effective_color = color if color is not None else self._defaults.get("color")
            button = _build_button("link", label, effective_row, effective_color, url=url)
            if button:
                self._pending.append(button)

        def add_action(self, label: str, action_id: str, row: Optional[int] = None, color: Optional[str] = None) -> None:
            """Queue an action button during progressive collection."""
            if self._pending is None:
                logger.warning("session.button.add_action() called without session.button.begin()")
                return
            effective_row = row if row is not None else self._defaults.get("row", 1)
            effective_color = color if color is not None else self._defaults.get("color")
            button = _build_button("action", label, effective_row, effective_color, action_id=action_id)
            if button:
                self._pending.append(button)

        add_link_button = add_link
        add_action_button = add_action

        def end(self) -> None:
            """Finalize and stream the progressive button block."""
            if self._pending is None:
                logger.warning("session.button.end() called without session.button.begin()")
                return

            if not self._pending:
                logger.warning("session.button.end() called but no buttons were added; skipping block.")
                self._pending = None
                self._defaults = {"row": 1, "color": None}
                return

            payload = _render_button_block(self._pending)
            self._session._handler.stream(self._session._data, payload)

            self._pending = None
            self._defaults = {"row": 1, "color": None}
            logger.debug("Progressive buttons block streamed and cleared.")

        # Alias for developer preference
        def pass_image(self, url: str) -> None:
            self.image(url)

        # Tracing helper: wrap content with lexia tracing markers
        def tracing(self, content: str, visibility: str = "all") -> None:
            """
            Send tracing information with visibility control.
            
            Args:
                content: The tracing text content to display
                visibility: Who can see this trace - "all" or "admin" (default: "all")
            """
            if not content:
                return
            
            # Validate visibility parameter
            if visibility not in ("all", "admin"):
                logger.warning(f"Invalid visibility '{visibility}', defaulting to 'all'")
                visibility = "all"
            
            payload = f"[lexia.tracing.start]\n- visibility: {visibility}\ncontent: {content}\n[lexia.tracing.end]"
            self._handler.stream(self._data, payload)
        
        # Progressive tracing API
        def tracing_begin(self, message: str, visibility: str = "all") -> None:
            """
            Start a progressive trace block that can be built incrementally.
            
            Use this when you want to build a single trace entry over time,
            updating it as progress happens, rather than creating multiple
            separate trace entries.
            
            Args:
                message: Initial message to start the trace with
                visibility: Who can see this trace - "all" or "admin" (default: "all")
            
            Example:
                session.tracing_begin("🔄 Processing chunks:", "all")
                for i in range(10):
                    session.tracing_append(f"\\n  • Chunk {i+1}/10...")
                    # ... do work ...
                    session.tracing_append(f" ✓")
                session.tracing_end("\\n✅ All done!")
            """
            if not message:
                return
            
            # Validate visibility
            if visibility not in ("all", "admin"):
                logger.warning(f"Invalid visibility '{visibility}', defaulting to 'all'")
                visibility = "all"
            
            # Initialize progressive trace buffer
            self._progressive_trace_buffer = message
            self._progressive_trace_visibility = visibility
            logger.debug(f"Progressive trace started with visibility '{visibility}'")
        
        def tracing_append(self, message: str) -> None:
            """
            Append content to the current progressive trace block.
            
            Must be called after tracing_begin(). Appends the message to
            the internal buffer. The complete trace will be sent when
            tracing_end() is called.
            
            Args:
                message: Content to append to the progressive trace
            
            Example:
                session.tracing_begin("Processing:")
                session.tracing_append("\\n  - Step 1 done")
                session.tracing_append("\\n  - Step 2 done")
                session.tracing_end()
            """
            if self._progressive_trace_buffer is None:
                logger.warning("tracing_append() called without tracing_begin(). Call tracing_begin() first.")
                return
            
            if not message:
                return
            
            # Append to buffer
            self._progressive_trace_buffer += message
            logger.debug(f"Appended to progressive trace: {len(message)} chars")
        
        def tracing_end(self, message: str = None) -> None:
            """
            Complete and send the progressive trace block.
            
            Optionally append a final message, then send the complete
            trace content as a single trace entry.
            
            Args:
                message: Optional final message to append before sending
            
            Example:
                session.tracing_begin("Processing items:")
                for item in items:
                    session.tracing_append(f"\\n  • {item}...")
                    process(item)
                    session.tracing_append(" ✓")
                session.tracing_end("\\n✅ Complete!")
            """
            if self._progressive_trace_buffer is None:
                logger.warning("tracing_end() called without tracing_begin(). Nothing to send.")
                return
            
            # Append optional final message
            if message:
                self._progressive_trace_buffer += message
            
            # Send the complete trace
            complete_content = self._progressive_trace_buffer
            visibility = self._progressive_trace_visibility
            
            # Clear buffer
            self._progressive_trace_buffer = None
            self._progressive_trace_visibility = "all"
            
            # Send as a single trace entry
            self.tracing(complete_content, visibility)
            logger.debug(f"Progressive trace completed and sent: {len(complete_content)} chars")

    def begin(self, data) -> '_Session':
        """
        Start a streaming session bound to a single response.
        Returns a session with stream()/close()/error() methods.
        """
        return LexiaHandler._Session(self, data)
    
    def update_centrifugo_config(self, stream_url: str, stream_token: str):
        """
        Update Centrifugo configuration with dynamic values from request.
        Only applicable in production mode.
        
        Args:
            stream_url: Centrifugo server URL from request
            stream_token: Centrifugo API key from request
        """
        if self.dev_mode:
            logger.debug("Dev mode active - skipping Centrifugo config update")
            return
        
        if stream_url and stream_token:
            self.stream_client.update_config(stream_url, stream_token)
            logger.info(f"Updated Centrifugo config - URL: {stream_url}")
        else:
            logger.warning("Stream URL or token not provided, using default configuration")
    
    def stream_chunk(self, data, content: str):
        """
        Stream a chunk of AI response.
        Uses DevStreamClient in dev mode, Centrifugo in production.
        """
        logger.info(f"🟢 [3-HANDLER] stream_chunk() called with '{content}' ({len(content)} chars)")
        
        # Update config if dynamic values are provided (production only)
        if not self.dev_mode and hasattr(data, 'stream_url') and hasattr(data, 'stream_token'):
            self.update_centrifugo_config(data.stream_url, data.stream_token)
        
        self.stream_client.send_delta(data.channel, data.response_uuid, data.thread_id, content)
        logger.info(f"🟢 [4-HANDLER] Chunk sent to stream_client.send_delta()")
    
    # New simplified streaming API: accumulate + stream
    def stream(self, data, content: str) -> None:
        """Stream a chunk and aggregate it internally for later completion."""
        # Normalize semantic commands to markers when possible
        if isinstance(content, str):
            key = content.strip().lower()
            content = self._marker_aliases.get(key, content)
        
        # Append to buffer (thread-safe)
        with self._buffers_lock:
            bucket = self._buffers.get(getattr(data, 'response_uuid', None))
            if bucket is None:
                bucket = []
                self._buffers[data.response_uuid] = bucket
            bucket.append(content)
        # Forward live chunk to clients
        self.stream_chunk(data, content)

    def _drain_buffer(self, response_uuid: str) -> str:
        """Join and clear the buffer for a response UUID (thread-safe)."""
        with self._buffers_lock:
            parts = self._buffers.pop(response_uuid, None)
        if not parts:
            return ""
        return "".join(parts)

    def complete_response(self, data, full_response: str, usage_info=None, file_url=None):
        """
        Complete AI response and send to Lexia.
        Uses DevStreamClient in dev mode, Centrifugo in production.
        """
        # Update config if dynamic values are provided (production only)
        if not self.dev_mode and hasattr(data, 'stream_url') and hasattr(data, 'stream_token'):
            self.update_centrifugo_config(data.stream_url, data.stream_token)
        
        # Send completion via appropriate streaming client
        self.stream_client.send_completion(data.channel, data.response_uuid, data.thread_id, full_response)
        
        # Create complete response with all required fields
        backend_data = create_complete_response(data.response_uuid, data.thread_id, full_response, usage_info, file_url)
        backend_data['conversation_id'] = data.conversation_id
        
        # Ensure required fields have proper values even if usage_info is missing
        if not usage_info or usage_info.get('prompt_tokens', 0) == 0:
            # Provide default values when usage info is missing
            backend_data['usage'] = {
                'input_tokens': 1,  # Minimum token count
                'output_tokens': len(full_response.split()) if full_response else 1,  # Estimate from response length
                'total_tokens': 1 + (len(full_response.split()) if full_response else 1),
                'input_token_details': {
                    'tokens': [{"token": "default", "logprob": 0.0}]
                },
                'output_token_details': {
                    'tokens': [{"token": "default", "logprob": 0.0}]
                }
            }
        
        # In dev mode, skip backend API call if URL is not provided
        if self.dev_mode and (not hasattr(data, 'url') or not data.url):
            logger.info("🔧 Dev mode: Skipping backend API call (no URL provided)")
            return
        
        # Extract headers from request data
        request_headers = {}
        if hasattr(data, 'headers') and data.headers:
            request_headers.update(data.headers)
            logger.info(f"Extracted headers from request: {request_headers}")
        
        # Skip if no URL provided (optional in dev mode)
        if not hasattr(data, 'url') or not data.url:
            logger.warning("⚠️  No URL provided, skipping backend API call")
            return
        
        logger.info(f"=== SENDING TO LEXIA API ===")
        logger.info(f"URL: {data.url}")
        logger.info(f"Headers: {request_headers}")
        logger.info(f"Data: {backend_data}")
        
        # Send to Lexia backend with headers
        try:
            response = self.api.post(data.url, backend_data, headers=request_headers)
            
            logger.info(f"=== LEXIA API RESPONSE ===")
            logger.info(f"Status Code: {response.status_code}")
            logger.info(f"Response Headers: {dict(response.headers)}")
            logger.info(f"Response Content: {response.text}")
            
            if response.status_code != 200:
                logger.error(f"LEXIA API ERROR: {response.status_code} - {response.text}")
            else:
                logger.info("✅ LEXIA API SUCCESS: Response accepted")
        except Exception as e:
            logger.error(f"Failed to send to Lexia API: {e}")
        
        # Update if different URL
        # if data.url_update and data.url_update != data.url:
        #     update_data = create_complete_response(data.response_uuid, data.thread_id, full_response, usage_info)
        #     update_data['conversation_id'] = data.conversation_id
            
        #     # Ensure update data also has proper usage values
        #     if not usage_info or usage_info.get('prompt_tokens', 0) == 0:
        #         update_data['usage'] = {
        #             'input_tokens': 1,
        #             'output_tokens': len(full_response.split()) if full_response else 1,
        #             'total_tokens': 1 + (len(full_response.split()) if full_response else 1),
        #             'input_token_details': {
        #                 'tokens': [{"token": "default", "logprob": 0.0}]
        #             },
        #             'output_token_details': {
        #                 'tokens': [{"token": "default", "logprob": 0.0}]
        #             }
        #         }
            
        #     logger.info(f"=== SENDING UPDATE TO LEXIA API ===")
        #     logger.info(f"Update URL: {data.url_update}")
        #     logger.info(f"Update Headers: {request_headers}")
        #     logger.info(f"Update Data: {update_data}")
            
        #     update_response = self.api.put(data.url_update, update_data, headers=request_headers)
            
        #     logger.info(f"=== LEXIA UPDATE API RESPONSE ===")
        #     logger.info(f"Update Status Code: {update_response.status_code}")
        #     logger.info(f"Update Response Content: {update_response.text}")
            
        #     if update_response.status_code != 200:
        #         logger.error(f"LEXIA UPDATE API ERROR: {update_response.status_code} - {update_response.text}")
        #     else:
        #         logger.info("✅ LEXIA UPDATE API SUCCESS: Update accepted")

    # New simplified close API: finalize using aggregated buffer
    def close(self, data, usage_info=None, file_url=None) -> str:
        """
        Finalize the response using the internally aggregated content.
        Returns the finalized full text for optional caller-side persistence.
        """
        full_response = self._drain_buffer(getattr(data, 'response_uuid', None))
        self.complete_response(data, full_response, usage_info, file_url)
        return full_response
    
    def send_error(self, data, error_message: str, trace: str = None, exception: Exception = None):
        """
        Send error message via streaming client and persist to backend API.
        Uses DevStreamClient in dev mode, Centrifugo in production.
        
        Args:
            data: Request data containing channel, UUID, thread_id, etc.
            error_message: Error message to send
            trace: Optional stack trace string
            exception: Optional exception object (will extract trace from it)
        """
        # Update config if dynamic values are provided (production only)
        if not self.dev_mode and hasattr(data, 'stream_url') and hasattr(data, 'stream_token'):
            self.update_centrifugo_config(data.stream_url, data.stream_token)
        
        # Format error message for display
        error_display_message = f"❌ **Error:** {error_message}"
        
        # In DEV mode: Stream exactly like normal responses (chunk + complete)
        if self.dev_mode:
            # Clear any pending aggregation for this response
            self._drain_buffer(getattr(data, 'response_uuid', None))
            # Stream the error message as chunks (same as normal content)
            self.stream_client.send_delta(data.channel, data.response_uuid, data.thread_id, error_display_message)
            # Complete the stream (same as normal completion)
            self.stream_client.send_completion(data.channel, data.response_uuid, data.thread_id, error_display_message)
            logger.info("🔧 Dev mode: Error streamed to frontend (delta + complete), skipping backend API calls")
            return
        
        # PRODUCTION mode: Different flow for Centrifugo
        # First stream the error as visible content
        self.stream_client.send_delta(data.channel, data.response_uuid, data.thread_id, error_display_message)
        # Then send error signal via Centrifugo
        self.stream_client.send_error(data.channel, data.response_uuid, data.thread_id, error_message)
        # Clear any pending aggregation for this response
        self._drain_buffer(getattr(data, 'response_uuid', None))
        
        # Skip if no URL provided (production mode only)
        if not hasattr(data, 'url') or not data.url:
            logger.warning("⚠️  No URL provided, skipping error API call")
            return
        
        # Also persist error to backend API (like previous implementation)
        error_response = {
            'uuid': data.response_uuid,
            'conversation_id': data.conversation_id,
            'content': error_message,
            'role': 'developer',
            'status': 'FAILED',
            'usage': {
                'input_tokens': 0,
                'output_tokens': 0,
                'total_tokens': 0,
                'input_token_details': {
                    'tokens': []
                },
                'output_token_details': {
                    'tokens': []
                }
            }
        }
        
        # Extract headers from request data
        request_headers = {}
        if hasattr(data, 'headers') and data.headers:
            request_headers.update(data.headers)
            logger.info(f"Extracted headers from request for error: {request_headers}")
        
        logger.info(f"=== SENDING ERROR TO LEXIA API ===")
        logger.info(f"URL: {data.url}")
        logger.info(f"Headers: {request_headers}")
        logger.info(f"Error Data: {error_response}")
        
        # Send error to Lexia backend with headers
        try:
            response = self.api.post(data.url, error_response, headers=request_headers)
            
            logger.info(f"=== LEXIA ERROR API RESPONSE ===")
            logger.info(f"Status Code: {response.status_code}")
            logger.info(f"Response Headers: {dict(response.headers)}")
            logger.info(f"Response Content: {response.text}")
            
            if response.status_code != 200:
                logger.error(f"LEXIA ERROR API FAILED: {response.status_code} - {response.text}")
            else:
                logger.info("✅ LEXIA ERROR API SUCCESS: Error persisted to backend")
        except Exception as e:
            logger.error(f"Failed to persist error to backend API: {e}")
        
        # Also send error to logging endpoint (api/internal/v1/logs)
        try:
            # Extract base URL from data.url
            parsed_url = urlparse(data.url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            log_url = f"{base_url}/api/internal/v1/logs"
            
            # Get stack trace from various sources
            trace_info = ''
            if trace:
                # Use provided trace string
                trace_info = trace
            elif exception:
                # Extract trace from exception object
                trace_info = ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))
            else:
                # Try to get current exception context
                exc_info = traceback.format_exc()
                if exc_info and exc_info != 'NoneType: None\n':
                    trace_info = exc_info
            
            # Prepare log payload according to Laravel API spec
            log_payload = {
                'message': error_message[:1000],  # Max 1000 chars as per validation
                'trace': trace_info[:5000] if trace_info else '',  # Max 5000 chars as per validation
                'level': 'error',  # error, warning, info, or critical
                'where': 'lexia-sdk',  # Where the error occurred
                'additional': {
                    'uuid': data.response_uuid,
                    'conversation_id': data.conversation_id,
                    'thread_id': data.thread_id,
                    'channel': data.channel
                }
            }
            
            logger.info(f"=== SENDING ERROR LOG TO LEXIA ===")
            logger.info(f"Log URL: {log_url}")
            logger.info(f"Log Payload: {log_payload}")
            
            # Send to logging endpoint
            log_response = self.api.post(log_url, log_payload, headers=request_headers)
            
            logger.info(f"=== LEXIA LOG API RESPONSE ===")
            logger.info(f"Status Code: {log_response.status_code}")
            logger.info(f"Response Content: {log_response.text}")
            
            if log_response.status_code != 200:
                logger.error(f"LEXIA LOG API FAILED: {log_response.status_code} - {log_response.text}")
            else:
                logger.info("✅ LEXIA LOG API SUCCESS: Error logged to backend")
        except Exception as e:
            logger.error(f"Failed to send error log to Lexia: {e}")
