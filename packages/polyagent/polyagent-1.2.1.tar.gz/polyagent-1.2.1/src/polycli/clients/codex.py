"""Codex CLI client."""

import json
import subprocess
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import os

from .base import BaseClient
from ..adapters import RunResult
from ..message import Message


class CodexClient(BaseClient):
    """Client for Codex CLI."""

    @classmethod
    def name(cls) -> str:
        return "codex"

    @classmethod
    def is_available(cls) -> bool:
        """Check if codex command is available."""
        import shutil
        return shutil.which('codex') is not None

    @classmethod
    def run_cli(cls,
                agent: 'PolyAgent',
                prompt: str,
                system_prompt: Optional[str],
                ephemeral: bool) -> RunResult:
        """Run using Codex CLI with stateless session approach."""
        if agent.debug:
            print(f"[DEBUG] Running with Codex CLI")

        # Generate session UUID for this run
        session_id = str(uuid.uuid4())

        # Prepare session directory (~/.codex/sessions/YYYY/MM/DD/)
        now = datetime.now(timezone.utc)
        session_dir = Path.home() / '.codex' / 'sessions' / f"{now.year:04d}" / f"{now.month:02d}" / f"{now.day:02d}"
        session_dir.mkdir(parents=True, exist_ok=True)

        # Create session filename (rollout-TIMESTAMP-UUID.jsonl)
        timestamp_str = now.strftime("%Y-%m-%dT%H-%M-%S")
        session_file = session_dir / f"rollout-{timestamp_str}-{session_id}.jsonl"

        # Always create session file (even if empty) since we always use resume
        # Convert messages to Codex format (will include session_meta even if no messages)
        codex_messages = agent.messages.to_format("codex", session_id=session_id, cwd=agent.cwd)

        with open(session_file, 'w', encoding='utf-8') as f:
            for msg in codex_messages:
                f.write(json.dumps(msg, ensure_ascii=False) + '\n')

        # Remember how many lines we wrote (including metadata)
        lines_written = len(codex_messages)

        if agent.debug:
            print(f"[DEBUG] Created Codex session file: {session_file}")
            print(f"[DEBUG] Wrote {lines_written} lines to session")

        # Build Codex command - always use exec resume with our own session
        # Since we create our own session file, we always "resume" it
        cmd = ['codex', 'exec', '--dangerously-bypass-approvals-and-sandbox', 'resume', session_id, prompt]

        # Add system prompt if provided (may need different approach for Codex)
        if system_prompt:
            # Note: Codex may not have direct system prompt support
            # Could prepend to first message instead
            pass

        if agent.debug:
            print(f"[DEBUG] Running command: {' '.join(cmd)}")

        try:
            # Run Codex command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=agent.cwd
            )

            if agent.debug:
                print(f"[DEBUG] Codex return code: {result.returncode}")
                if result.stderr:
                    print(f"[DEBUG] Codex stderr: {result.stderr}")

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or "Unknown error"
                return RunResult({
                    "status": "error",
                    "message": f"Codex failed: {error_msg}"
                })

            # Parse response using helper function
            success, content = cls._parse_codex_output(result.stdout)

            if not success:
                return RunResult({
                    "status": "error",
                    "message": f"Codex failed: {content}"
                })

            if agent.debug:
                print(f"[DEBUG] Raw Codex output: {result.stdout[:500]}...")
                print(f"[DEBUG] Extracted content: {content}")

            # Update messages if not ephemeral - read from actual session file
            if not ephemeral:
                # Reload session file to get new messages
                if session_file.exists():
                    all_messages = []
                    with open(session_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip():
                                all_messages.append(json.loads(line))

                    if agent.debug:
                        print(f"[DEBUG] Total lines in Codex session file: {len(all_messages)}")
                        print(f"[DEBUG] Lines we wrote: {lines_written}")

                    # Extract only NEW lines that Codex added (beyond what we wrote)
                    if len(all_messages) > lines_written:
                        new_lines = all_messages[lines_written:]

                        if agent.debug:
                            print(f"[DEBUG] New lines added by Codex: {len(new_lines)}")

                        # Convert Codex format messages to standard format
                        new_messages = cls._extract_messages_from_codex(new_lines)

                        if agent.debug:
                            print(f"[DEBUG] Adding {len(new_messages)} new messages from Codex")

                        # Add each new message
                        for new_msg in new_messages:
                            agent.messages.add_message(Message(new_msg, format="codex"))
                    else:
                        if agent.debug:
                            print(f"[DEBUG] No new lines added by Codex")
                else:
                    # No session file, manually add messages (fallback)
                    if agent.debug:
                        print(f"[DEBUG] Session file not found, manually adding messages")
                    agent.messages.add_user_message(prompt)
                    agent.messages.add_message(Message({
                        "role": "assistant",
                        "content": content
                    }, format="standard"))

            return RunResult({
                "status": "success",
                "result": content,
                "session_id": session_id,
                "model": "codex"
            })

        except subprocess.TimeoutExpired:
            return RunResult({
                "status": "error",
                "message": "Codex command timed out"
            })
        except Exception as e:
            return RunResult({
                "status": "error",
                "message": f"Codex error: {str(e)}"
            })
        finally:
            # Clean up session file if not debugging
            if session_file.exists() and not agent.debug:
                session_file.unlink()

    @classmethod
    def _parse_codex_output(cls, raw_output: str) -> tuple[bool, str]:
        """
        Parse Codex output to extract the actual response content.

        Returns:
            (success, content) - success is False if Codex indicated an error
        """
        if not raw_output:
            return False, "Empty response from Codex"

        lines = raw_output.strip().split('\n')

        # Check for error indicators
        if any(line.startswith("Error:") or line.startswith("error:") for line in lines):
            return False, raw_output

        # Extract the assistant's response (everything after "[timestamp] codex")
        in_response = False
        response_lines = []

        for line in lines:
            # Check if this is a codex response line (format: "[timestamp] codex")
            if '] codex' in line:
                in_response = True
                continue
            elif in_response:
                # Once we're in response, collect everything except "tokens used" line
                if line.startswith('[') and 'tokens used:' in line:
                    break  # End of response
                response_lines.append(line)

        if response_lines:
            # Join all lines, preserving the full response
            content = '\n'.join(response_lines).strip()
            return True, content

        # Fallback: couldn't parse, return full output
        return True, raw_output

    @classmethod
    def _extract_messages_from_codex(cls, codex_messages: List[Dict]) -> List[Dict]:
        """Extract conversation messages from Codex format."""
        result = []
        for msg in codex_messages:
            # Skip session metadata
            if msg.get('type') == 'session_meta':
                continue

            # Extract response_item payloads
            if msg.get('type') == 'response_item' and 'payload' in msg:
                payload = msg['payload']
                # Skip environment context
                if payload.get('type') == 'message':
                    # Check if it's environment context
                    content = payload.get('content', [])
                    if content and len(content) == 1 and '<environment_context>' in content[0].get('text', ''):
                        continue
                    # Add as message
                    result.append(msg)

        return result