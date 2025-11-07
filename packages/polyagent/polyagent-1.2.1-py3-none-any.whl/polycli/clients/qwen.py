"""Qwen Code CLI client."""

import shutil
import subprocess
import json
import tempfile
import os
import hashlib
import uuid
from pathlib import Path
from typing import Optional

from .base import BaseClient
from ..adapters import RunResult
from ..message import MessageList


class QwenClient(BaseClient):
    """Client for Qwen Code CLI."""

    @classmethod
    def name(cls) -> str:
        return "qwen-code"

    @classmethod
    def is_available(cls) -> bool:
        return shutil.which('qwen') is not None

    @classmethod
    def supports_model(cls, model: str) -> bool:
        # Qwen typically uses glm models or qwen models
        return any(x in model.lower() for x in ['qwen', 'glm'])

    @classmethod
    def run_cli(cls,
                agent: 'PolyAgent',
                prompt: str,
                model: str,
                system_prompt: Optional[str] = None,
                ephemeral: bool = False,
                **kwargs) -> RunResult:
        """Run using Qwen CLI - exact copy of _run_qwen_cli logic."""
        if agent.debug:
            print(f"[DEBUG] Running with Qwen CLI, model: {model}")

        if not agent._qwen_cmd:
            return RunResult({"status": "error", "message": "Qwen CLI not found"})

        # Get model configuration
        from ..utils.model_config import get_model_config
        model_cfg = get_model_config().get_model(model)
        if not model_cfg:
            return RunResult({"status": "error", "message": f"Model '{model}' not configured"})

        # Prepare messages for checkpoint
        messages_to_save = []
        effective_system = system_prompt or agent.system_prompt

        if len(agent.messages) > 0:
            # Convert existing messages to standard format
            messages_to_save = agent.messages.to_format("standard")

        # Inject system prompt if needed
        if effective_system:
            system_user = {"role": "user", "content": f"[System]: {effective_system}"}
            system_assistant = {"role": "assistant", "content": "I understand and will follow these instructions."}

            # Check if we need to replace or inject
            if len(messages_to_save) >= 2 and "[System]:" in str(messages_to_save[0].get('content', '')):
                messages_to_save[0] = system_user
                messages_to_save[1] = system_assistant
            else:
                messages_to_save = [system_user, system_assistant] + messages_to_save

        # Create checkpoint file if we have messages
        checkpoint_file = None
        if messages_to_save:
            # Convert to Qwen format with consecutive user merging
            temp_list = MessageList(messages_to_save)
            qwen_messages = temp_list.to_format("qwen", merge_consecutive=True)

            # Save checkpoint
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
                json.dump(qwen_messages, f, ensure_ascii=False)
                checkpoint_file = f.name

        # Generate unique save tag
        save_tag = f"polycli-{uuid.uuid4().hex[:8]}"

        # Track what we're sending to Qwen (after merging)
        messages_sent_count = len(qwen_messages) if checkpoint_file else 0

        try:
            # Build command
            cmd = [
                agent._qwen_cmd,
                '--save', save_tag,
                '--yolo',
                '--openai-api-key', model_cfg['api_key'],
                '--openai-base-url', model_cfg['endpoint'],
                '--model', model_cfg['model']
            ]

            if checkpoint_file:
                cmd.extend(['--resume', checkpoint_file])

            # Set environment
            env = os.environ.copy()
            env.update({
                'OPENAI_MODEL': model_cfg['model'],
                'OPENAI_API_KEY': model_cfg['api_key'],
                'OPENAI_BASE_URL': model_cfg['endpoint']
            })

            # Run command
            result = subprocess.run(
                cmd,
                input=prompt,
                capture_output=True,
                text=True,
                cwd=agent.cwd,
                env=env,
                encoding='utf-8'
            )

            if result.returncode == 0:
                # Load saved checkpoint if not ephemeral
                if not ephemeral:
                    project_hash = hashlib.sha256(agent.cwd.encode()).hexdigest()
                    qwen_dir = Path.home() / ".qwen" / "tmp" / project_hash
                    saved_checkpoint = qwen_dir / f"checkpoint-{save_tag}.json"

                    if saved_checkpoint.exists():
                        with open(saved_checkpoint, 'r', encoding='utf-8') as f:
                            new_messages = json.load(f)

                        # Track original count before removing system prompt
                        original_new_count = len(new_messages)
                        system_removed = False

                        # Remove injected system prompt if present
                        if effective_system and len(new_messages) >= 2:
                            if "[System]:" in str(new_messages[0].get('parts', [{}])[0].get('text', '')):
                                new_messages = new_messages[2:]
                                system_removed = True

                        # Adjust expected count if we removed system messages
                        expected_count = messages_sent_count
                        if system_removed and messages_sent_count > 0:
                            # We sent messages WITH system, but removed it from response
                            expected_count = messages_sent_count - 2

                        # Only append NEW messages (those after what we sent)
                        if agent.debug:
                            print(f"[DEBUG] Checkpoint has {len(new_messages)} messages (was {original_new_count}), expected {expected_count} existing")

                        if len(new_messages) > expected_count:
                            # Get only the new messages (prompt + response)
                            new_msgs_only = new_messages[expected_count:]
                            if agent.debug:
                                print(f"[DEBUG] Adding {len(new_msgs_only)} new messages")

                            # Add them to our MessageList
                            for msg in new_msgs_only:
                                agent.messages.add_message(msg)
                        else:
                            if agent.debug:
                                print(f"[DEBUG] No new messages to add")

                        # Clean up (configurable)
                        if not os.environ.get('POLYCLI_KEEP_CHECKPOINTS'):
                            saved_checkpoint.unlink()
                        else:
                            print(f"[DEBUG] Keeping checkpoint file: {saved_checkpoint}")

                # Extract last response
                last_response = result.stdout.strip()

                return RunResult({
                    "status": "success",
                    "message": {"role": "assistant", "content": last_response},
                    "type": "assistant"
                })
            else:
                return RunResult({
                    "status": "error",
                    "message": f"Qwen CLI failed: {result.stderr}"
                })

        finally:
            if checkpoint_file and os.path.exists(checkpoint_file):
                if not os.environ.get('POLYCLI_KEEP_CHECKPOINTS'):
                    os.unlink(checkpoint_file)
                else:
                    print(f"[DEBUG] Keeping input checkpoint file: {checkpoint_file}")