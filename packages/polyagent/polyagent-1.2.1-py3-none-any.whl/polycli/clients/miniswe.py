"""Mini-SWE agent client (Python library, not CLI)."""

import platform
from typing import Optional, Type, Callable
from pydantic import BaseModel

from .base import BaseClient
from ..adapters import RunResult


class MiniSweClient(BaseClient):
    """Client for Mini-SWE agent (Python package)."""

    @classmethod
    def name(cls) -> str:
        return "mini-swe"

    @classmethod
    def is_available(cls) -> bool:
        """Check if mini-swe-agent package is installed."""
        try:
            import minisweagent
            return True
        except ImportError:
            return False

    @classmethod
    def supports_model(cls, model: str) -> bool:
        # Mini-SWE can use any model via CustomMiniSweModel
        return True

    @classmethod
    def run_cli(cls,
                agent: 'PolyAgent',
                prompt: str,
                model: str,
                system_prompt: Optional[str],
                ephemeral: bool,
                schema_cls: Optional[Type[BaseModel]],
                memory_serializer: Optional[Callable]) -> RunResult:
        """Run using Mini-SWE agent - exact copy of _run_mini_swe logic."""
        if agent.debug:
            print(f"[DEBUG] Running with Mini-SWE, model: {model}")

        # Import Mini-SWE dependencies
        try:
            from minisweagent.agents.default import DefaultAgent
            from minisweagent.environments.local import LocalEnvironment
            from ..utils.llm_client import CustomMiniSweModel
        except ImportError:
            return RunResult({
                "status": "error",
                "message": "Mini-SWE not installed"
            })

        # @@@ macOS fix - Use printf on macOS (subprocess uses /bin/sh which doesn't support echo -e)
        if platform.system() == 'Darwin':
            instance_template = (
                "Your task: {{task}}. Please reply with a single shell command in triple backticks with 'bash' language tag (```bash). "
                "Use printf (not echo) for output. "
                "To finish, the first line of the output must be 'COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT'. "
                "Example: printf 'COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT\\nYour result\\n'"
            )
        else:
            instance_template = (
                "Your task: {{task}}. Please reply with a single shell command in triple backticks with 'bash' language tag (```bash). "
                "To finish, the first line of the output of the shell command must be 'COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT'."
            )

        # Create Mini-SWE agent with config
        temp_agent = DefaultAgent(
            CustomMiniSweModel(model_name=model),
            LocalEnvironment(cwd=agent.cwd),
            step_limit=10,
            system_template=system_prompt if system_prompt else "You are a helpful assistant that can do anything.",
            instance_template=instance_template
        )

        # Prepare input with history
        if len(agent.messages) > 0:
            # Convert messages to standard format
            history = []
            for msg in agent.messages:
                if msg.content:
                    role = "assistant" if msg.role == "model" else msg.role
                    history.append({"role": role, "content": msg.content})

            # Format as conversation
            input_text = ""
            for msg in history:
                input_text += f"{msg['role']}: {msg['content']}\n"
            input_text += f"user: {prompt}"
        else:
            input_text = prompt

        # Run agent
        status, message = temp_agent.run(input_text)

        # Update messages if not ephemeral
        if not ephemeral:
            agent.messages.add_message({"role": "user", "content": prompt})
            # Add agent messages (skip first two which are system messages)
            for msg in temp_agent.messages[2:]:
                agent.messages.add_message(msg)

        return RunResult({
            "status": status,
            "message": {"role": "assistant", "content": message},
            "type": "assistant"
        })