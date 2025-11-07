"""API client for direct LLM API calls (no CLI)."""

from typing import Optional, Generator, Any, Type, Callable
from pydantic import BaseModel

from .base import BaseClient
from ..adapters import RunResult
from ..utils.llm_client import get_llm_client
from ..utils.serializers import default_json_serializer


class ApiClient(BaseClient):
    """Client for direct API calls (no CLI tool needed)."""

    @classmethod
    def name(cls) -> str:
        return "no-tools"

    @classmethod
    def is_available(cls) -> bool:
        """API client is always available (just needs network)."""
        return True

    @classmethod
    def run_cli(cls,
                agent: 'PolyAgent',
                prompt: str,
                model: str,
                system_prompt: Optional[str] = None,
                ephemeral: bool = False,
                schema_cls: Optional[Type[BaseModel]] = None,
                memory_serializer: Optional[Callable] = None,
                stream: bool = False,
                **kwargs) -> RunResult:
        """Run using direct API calls - exact copy of _run_api logic."""
        if agent.debug:
            print(f"[DEBUG] Running with API, model: {model}")

        # Get LLM client
        try:
            llm_client, actual_model = get_llm_client(model)
        except Exception as e:
            return RunResult({"status": "error", "message": str(e)})

        # Prepare messages
        messages = []

        # Add system prompt
        effective_system = system_prompt or agent.system_prompt
        if effective_system:
            messages.append({"role": "system", "content": effective_system})

        # Add conversation history (convert to standard format)
        for msg in agent.messages:
            if msg.content:
                role = "assistant" if msg.role == "model" else msg.role
                messages.append({"role": role, "content": msg.content})

        # Add current prompt
        messages.append({"role": "user", "content": prompt})

        try:
            if schema_cls:
                # Structured output (no streaming support)
                if stream:
                    if agent.debug:
                        print("[DEBUG] Streaming not supported for structured output, ignoring stream=True")

                result = llm_client.chat.completions.create(
                    response_model=schema_cls,
                    model=actual_model,
                    messages=messages,
                    **kwargs
                )

                # Serialize response
                serializer = memory_serializer or default_json_serializer
                response_text = serializer(result)

                # Update messages if not ephemeral
                if not ephemeral:
                    agent.messages.add_message({"role": "user", "content": prompt})
                    agent.messages.add_message({
                        "role": "assistant",
                        "content": f"[Structured response ({schema_cls.__name__})]\n{response_text}"
                    })

                return RunResult({
                    "status": "success",
                    "result": result.model_dump(),
                    "type": "structured",
                    "schema": schema_cls.__name__
                })
            else:
                # Plain text response
                if stream:
                    # Use streaming
                    if agent.debug:
                        print("[DEBUG] Using streaming for API call")
                    response_content = cls._stream_tokens(agent, messages, model, **kwargs)
                else:
                    # Regular non-streaming call
                    result = llm_client.chat.completions.create(
                        model=actual_model,
                        messages=messages,
                        **kwargs
                    )

                    response_content = ""
                    if result and result.choices and result.choices[0].message:
                        response_content = result.choices[0].message.content or ""

                # Update messages if not ephemeral
                if not ephemeral:
                    agent.messages.add_message({"role": "user", "content": prompt})
                    agent.messages.add_message({"role": "assistant", "content": response_content})

                return RunResult({
                    "status": "success",
                    "message": {"role": "assistant", "content": response_content},
                    "type": "assistant"
                })

        except Exception as e:
            return RunResult({
                "status": "error",
                "message": f"API call failed: {str(e)}"
            })

    @classmethod
    def _stream_tokens(cls, agent, messages: list, model: str, **kwargs) -> str:
        """Simple synchronous streaming function - exact copy of _stream_tokens."""
        from ..utils.llm_client import get_llm_client

        # Get LLM client
        llm_client, actual_model = get_llm_client(model)

        full_response = ""

        # Get current session if exists
        try:
            from ..orchestration.orchestration import _current_session
            session = _current_session.get()
        except:
            session = None

        if agent.debug:
            print(f"[DEBUG] Starting streaming with model: {actual_model}")

        # Use the ConfiguredClient's create method - sync call with streaming
        response = llm_client.create(
            model=actual_model,
            messages=messages,
            stream=True,
            **kwargs
        )

        # Regular sync iteration over chunks
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content
                full_response += token

                # Publish if in session
                if session and hasattr(session, 'publish_tokens'):
                    session.publish_tokens(agent.id or "agent", token)

        return full_response