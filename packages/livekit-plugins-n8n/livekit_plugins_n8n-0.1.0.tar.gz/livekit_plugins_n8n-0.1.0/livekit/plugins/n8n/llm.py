from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional

import aiohttp

from livekit.agents import (
    APIConnectionError,
    APIStatusError,
    llm,
)
from livekit.agents.llm import FunctionTool, ToolChoice
from livekit.agents.types import (
    DEFAULT_API_CONNECT_OPTIONS,
    NOT_GIVEN,
    APIConnectOptions,
    NotGivenOr,
)

from .log import logger


@dataclass
class LLMOptions:
    """Configuration options for the n8n LLM integration."""
    webhook_url: str
    session_id: str = ""
    participant_identity: str = "unknown_user"


class LLMStream(llm.LLMStream):
    """
    Handles the non-streaming, single JSON response from the n8n webhook.
    """
    def __init__(
        self,
        llm: "LLM",
        *,
        n8n_response_future: aiohttp.ClientResponse,
        chat_ctx: llm.ChatContext,
        conn_options: APIConnectOptions,
        tools: list[FunctionTool] | None = None,
    ) -> None:
        super().__init__(llm, chat_ctx=chat_ctx, conn_options=conn_options, tools=tools)
        self._n8n_response_future = n8n_response_future

    async def _run(self) -> None:
        """Run the LLM stream, processing the single JSON response from the n8n webhook."""
        retryable = True
        response = None
        first_response = True
        try:
            # Wait for the full response
            response = await self._n8n_response_future

            if response.status != 200:
                error_text = await response.text()
                raise APIStatusError(
                    f"n8n Webhook API error: {error_text}",
                    status_code=response.status,
                    body=error_text,
                )

            # Parse the full JSON response
            data = await response.json()
            retryable = False

            # Expected format: [{"output": "..."}] or {"output": "..."}
            if isinstance(data, list) and len(data) > 0:
                full_text = data[0].get("output", "")
            elif isinstance(data, dict):
                full_text = data.get("output", "")
            else:
                raise ValueError(f"Unexpected response format from n8n: {data}")

            if not full_text:
                raise ValueError(f"No output field in n8n response: {data}")

            # Generate a unique request ID for this response
            request_id = str(uuid.uuid4())

            if first_response:
                logger.info("llm first response")
                first_response = False

            # Create a properly structured ChatChunk with ChoiceDelta
            chunk = llm.ChatChunk(
                id=request_id,
                delta=llm.ChoiceDelta(
                    role="assistant",
                    content=full_text,
                ),
            )
            
            # Send the chunk
            self._event_ch.send_nowait(chunk)
            
            logger.info("llm end")

        except aiohttp.ClientError as e:
            logger.error(f"Network error: {e}")
            raise APIConnectionError(retryable=retryable) from e
        except Exception as e:
            logger.error(f"Error processing n8n response: {e}")
            raise APIConnectionError(retryable=retryable) from e
        finally:
            if response:
                response.close()


class LLM(llm.LLM):
    """
    A custom LiveKit LLM implementation that communicates with an n8n webhook.
    This version is for non-streaming n8n webhooks that return a single JSON response.
    """
    def __init__(
        self,
        *,
        webhook_url: str | None = None,
        session_id: str | None = None,
        participant_identity: str | None = None,
    ) -> None:
        """
        Create a new instance of the n8n Webhook LLM.

        Args:
            webhook_url: The full URL of the n8n webhook. Defaults to N8N_WEBHOOK_URL env var.
            session_id: The session ID to use for conversation tracking. Defaults to "default_session".
            participant_identity: The participant's identity. Defaults to "unknown_user".
        """
        super().__init__()
        self._session: Optional[aiohttp.ClientSession] = None

        url = webhook_url or os.environ.get("N8N_WEBHOOK_URL")
        if url is None:
            raise ValueError("webhook_url or N8N_WEBHOOK_URL environment variable is required")

        self._opts = LLMOptions(
            webhook_url=url,
            session_id=session_id or "default_session",
            participant_identity=participant_identity or "unknown_user",
        )

    def ensure_session(self) -> None:
        """Ensure that the aiohttp client session is created."""
        if self._session is None:
            self._session = aiohttp.ClientSession()

    async def close(self) -> None:
        """Close the LLM client and cleanup resources."""
        if self._session is not None:
            await self._session.close()
            self._session = None

    def chat(
        self,
        *,
        chat_ctx: llm.ChatContext,
        conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS,
        tools: list[FunctionTool] | None = None,
        parallel_tool_calls: NotGivenOr[bool] = NOT_GIVEN,
        tool_choice: NotGivenOr[ToolChoice] = NOT_GIVEN,
        extra_kwargs: NotGivenOr[dict[str, Any]] = NOT_GIVEN,
    ) -> LLMStream:
        """Start a chat completion by sending a request to the n8n webhook."""
        # Extract the last user message
        last_message = next(
            (msg for msg in reversed(chat_ctx.items) if msg.role == "user"), None
        )
        if not last_message:
            raise ValueError("No user message found in chat context")

        # Get the text content from the message
        text_content = ""
        if hasattr(last_message, 'content'):
            if isinstance(last_message.content, str):
                text_content = last_message.content
            elif isinstance(last_message.content, list):
                # Join all text content items
                text_content = " ".join(
                    item if isinstance(item, str) else str(item)
                    for item in last_message.content
                )

        # Prepare the request payload
        payload = {
            "query": text_content,
            "session_id": self._opts.session_id,
            "user_identity": self._opts.participant_identity,
        }

        # Ensure the session is created
        self.ensure_session()

        logger.info("llm start", extra={"query": text_content, "session_id": self._opts.session_id})

        # Initiate the POST request
        response_future = self._session.post(
            self._opts.webhook_url,
            json=payload,
        )

        return LLMStream(
            self,
            n8n_response_future=response_future,
            chat_ctx=chat_ctx,
            conn_options=conn_options,
            tools=tools,
        )

    def set_session_id(self, session_id: str) -> None:
        """Update the session ID for conversation tracking."""
        self._opts.session_id = session_id

    def set_participant_identity(self, participant_identity: str) -> None:
        """Update the participant identity."""
        self._opts.participant_identity = participant_identity

    @classmethod
    def from_env(cls, **kwargs) -> LLM:
        """Create an N8nLLM instance from environment variables."""
        webhook_url = os.getenv("N8N_WEBHOOK_URL")
        if not webhook_url:
            raise ValueError("N8N_WEBHOOK_URL environment variable is required")

        return cls(webhook_url=webhook_url, **kwargs)