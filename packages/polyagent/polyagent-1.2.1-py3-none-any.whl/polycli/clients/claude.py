"""Claude Code CLI client."""

import shutil
import subprocess
import json
import time
from pathlib import Path
from typing import Optional, Generator, Any
from datetime import datetime

from .base import BaseClient
from ..adapters import RunResult
from ..message import Message
from ..event import ClientEvent


class ClaudeClient(BaseClient):
    """Client for Claude Code CLI."""

    @classmethod
    def name(cls) -> str:
        return "claude-code"

    @classmethod
    def is_available(cls) -> bool:
        return shutil.which('claude') is not None

    @classmethod
    def supports_model(cls, model: str) -> bool:
        return 'claude' in model.lower()

    @classmethod
    def run_cli(cls,
                agent: 'PolyAgent',
                prompt: str,
                system_prompt: Optional[str] = None,
                ephemeral: bool = False,
                stream_events: bool = False,
                **kwargs):
        """
        Run Claude CLI - exact copy of _run_claude_cli logic.

        Returns:
            Generator when stream_events=True
            RunResult when stream_events=False
        """
        if stream_events:
            # Return the generator itself
            return cls._run_generator(agent, prompt, system_prompt, ephemeral)
        else:
            # Consume generator and return just the RunResult
            for item in cls._run_generator(agent, prompt, system_prompt, ephemeral):
                if isinstance(item, RunResult):
                    return item  # Direct return, not yield!

    @classmethod
    def _run_generator(cls, agent, prompt: str, system_prompt: Optional[str], ephemeral: bool):
        """Internal generator - exact copy of _run_claude_cli_generator."""
        if agent.debug:
            print("[DEBUG] Running with Claude CLI")

        # Check availability
        if not agent._claude_cmd:
            yield RunResult({"status": "error", "message": "Claude CLI not found"})
            return

        # Prepare session management
        claude_projects_dir = Path.home() / ".claude" / "projects"
        cwd_encoded = agent._encode_path(agent.cwd)
        session_dir = claude_projects_dir / cwd_encoded

        # If we have messages, we need to resume (even for ephemeral)
        resume_id = None
        if len(agent.messages) > 0:
            last_msg = agent.messages[-1]
            if hasattr(last_msg, 'metadata') and last_msg.metadata:
                resume_id = last_msg.metadata.get('sessionId')
            if not resume_id:
                # Generate a fake session ID for loaded conversations
                import uuid
                resume_id = str(uuid.uuid4())
                if agent.debug:
                    print(f"[DEBUG] Generated resume ID for loaded conversation: {resume_id}")

        # Build command
        cmd = [agent._claude_cmd, prompt, '-p', '--output-format', 'json', '--dangerously-skip-permissions']

        # Add system prompt
        effective_system = system_prompt or agent.system_prompt
        if effective_system:
            cmd.extend(['--system-prompt', effective_system])

        session_file = None
        try:
            if resume_id:
                # Resume conversation - create session file with history
                if agent.debug:
                    print(f"[DEBUG] Resuming session: {resume_id}")

                session_dir.mkdir(parents=True, exist_ok=True)
                session_file = session_dir / f"{resume_id}.jsonl"

                # Convert messages to Claude format
                claude_messages = agent.messages.to_format("claude", session_id=resume_id, cwd=agent.cwd)

                # Write session file
                with open(session_file, 'w', encoding='utf-8') as f:
                    for msg in claude_messages:
                        f.write(json.dumps(msg, ensure_ascii=False) + '\n')

                if agent.debug:
                    print(f"[DEBUG] Wrote {len(claude_messages)} messages to resume file")
                    print(f"[DEBUG] Current messages in memory: {len(agent.messages)}")

                cmd.extend(['--resume', resume_id])

            # Run command
            if agent.debug:
                print(f"[DEBUG] Running command: {' '.join(cmd)}")
                print(f"[DEBUG] Session file exists: {session_file.exists() if session_file else 'No session file'}")

            # @@@ Event streaming - always use non-blocking execution
            import uuid
            import os

            # Generate our own event file ID to avoid collisions
            event_file_id = str(uuid.uuid4())
            event_dir = Path('/tmp/polycli-events')
            event_file = event_dir / f'{event_file_id}.jsonl'

            # Pass event file ID to hook bridge via environment variable
            env = os.environ.copy()
            env['POLYCLI_EVENT_FILE_ID'] = event_file_id

            # Start process without blocking
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=agent.cwd,
                encoding='utf-8',
                env=env
            )

            # Monitor events while process runs
            if event_file_id:
                # No need to wait for file - we know exact path
                file_position = 0

                while process.poll() is None:  # Still running
                    if event_file.exists():
                        with open(event_file, 'r') as f:
                            f.seek(file_position)
                            for line in f:
                                if line.strip():
                                    try:
                                        event_data = json.loads(line)
                                        event = ClientEvent(
                                            session_id=event_data.get('session_id'),
                                            event_type=event_data.get('hook_event_name'),
                                            timestamp=datetime.fromisoformat(event_data.get('polycli_timestamp')),
                                            tool_name=event_data.get('tool_name'),
                                            tool_input=event_data.get('tool_input'),
                                            tool_response=event_data.get('tool_response')
                                        )
                                        yield event
                                    except Exception as e:
                                        if agent.debug:
                                            print(f"[DEBUG] Error parsing event: {e}")
                            file_position = f.tell()
                    time.sleep(0.05)  # 50ms polling

            # Get final output
            stdout, stderr = process.communicate()
            result = subprocess.CompletedProcess(cmd, process.returncode, stdout, stderr)

            if result.returncode == 0:
                response_data = json.loads(result.stdout)

                # Load updated conversation if not ephemeral
                if not ephemeral:
                    new_session_id = response_data.get('session_id')
                    if new_session_id:
                        new_session_file = session_dir / f"{new_session_id}.jsonl"
                        if new_session_file.exists():
                            # Load messages from Claude's session file, filtering out summaries
                            raw_messages = []
                            with open(new_session_file, 'r', encoding='utf-8') as f:
                                for line in f:
                                    if line.strip():
                                        msg = json.loads(line)
                                        # Filter out summary messages at load time
                                        if msg.get('type') != 'summary':
                                            raw_messages.append(msg)
                                        elif agent.debug:
                                            print(f"[DEBUG] Filtered out summary message during load")

                            # Extract only NEW messages from Claude response
                            existing_count = len(agent.messages)

                            if agent.debug:
                                print(f"[DEBUG] Messages before loading Claude response: {existing_count}")
                                print(f"[DEBUG] Total messages in Claude session file (after filtering): {len(raw_messages)}")

                            # Only append messages that are NEW
                            if len(raw_messages) > existing_count:
                                new_messages_only = raw_messages[existing_count:]
                                if agent.debug:
                                    print(f"[DEBUG] Adding {len(new_messages_only)} new messages from Claude")

                                # Append each new message incrementally, filtering out "No response requested."
                                for msg in new_messages_only:
                                    message_obj = Message(msg)

                                    # Skip assistant messages that are just "No response requested."
                                    if (message_obj.role == 'assistant' and
                                        message_obj.content.strip() == 'No response requested.'):
                                        if agent.debug:
                                            print(f"[DEBUG] Filtered out 'No response requested.' message")
                                        continue

                                    agent.messages.add_message(message_obj)
                            else:
                                if agent.debug:
                                    print(f"[DEBUG] No new messages to add from Claude response")

                            if agent.debug:
                                print(f"[DEBUG] Total messages after Claude response: {len(agent.messages)}")

                            # Clean up
                            new_session_file.unlink()
                else:
                    # Ephemeral mode - keep existing messages, don't add new ones
                    if agent.debug:
                        print(f"[DEBUG] Ephemeral mode - keeping {len(agent.messages)} existing messages")

                # Always yield result
                yield RunResult({
                    "result": response_data.get('result'),
                    "session_id": response_data.get('session_id'),
                    "model": "claude-code",
                    "_claude_metadata": response_data
                })
            else:
                # Always yield error result
                yield RunResult({
                    "status": "error",
                    "message": f"Claude CLI failed: {result.stderr}"
                })

        finally:
            # Clean up session file
            if session_file and session_file.exists():
                if agent.debug:
                    print(f"[DEBUG] NOT deleting session file for inspection: {session_file}")
                else:
                    session_file.unlink()

            # Clean up event file
            if 'event_file' in locals() and event_file.exists():
                if agent.debug:
                    print(f"[DEBUG] NOT deleting event file for inspection: {event_file}")
                else:
                    event_file.unlink()
                    if agent.debug:
                        print(f"[DEBUG] Cleaned up event file: {event_file}")
