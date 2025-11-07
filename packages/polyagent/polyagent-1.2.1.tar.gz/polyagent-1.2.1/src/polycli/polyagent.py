#!/usr/bin/env python3
"""
PolyAgent: A unified agent that works with all backends.
Built on single source of truth (MessageList) with format conversion.
"""

import json
import os
import sys
from pathlib import Path
import shutil
import hashlib
from typing import Optional, Type, Callable
from pydantic import BaseModel
from .message import MessageList, Message
from .adapters import RunResult
from .utils.llm_client import get_llm_client
from .utils.serializers import default_json_serializer
from .orchestration import pattern
from dataclasses import dataclass
from datetime import datetime
from .clients.claude import ClaudeClient
from .clients.api import ApiClient
from .clients.qwen import QwenClient
from .clients.miniswe import MiniSweClient
from .clients.codex import CodexClient


@pattern
def tracked_run(agent, prompt, **run_kwargs):
    """Pattern wrapper for tracked agent.run() calls."""
    # Call run without tracked to avoid recursion
    return agent.run(prompt, tracked=False, **run_kwargs)


class PolyAgent:
    """
    Unified agent that works with all backends through a single interface.
    
    Core principle: MessageList is the single source of truth.
    All format conversions happen only when sending to specific backends.
    """
    
    def __init__(self, debug=False, system_prompt=None, cwd=None, id=None, max_tokens=None):
        """
        Initialize PolyAgent.
        
        Args:
            debug: Enable debug output
            system_prompt: Default system prompt for all runs
            cwd: Working directory for CLI tools
            id: Unique identifier for the agent
            max_tokens: Default token limit for all runs
        """
        # Single source of truth for messages
        self.messages = MessageList()
        
        # Configuration
        self.debug = debug
        self.system_prompt = system_prompt
        self.cwd = str(Path(cwd)) if cwd else os.getcwd()
        self.id = id  # None if not provided
        self.max_tokens = max_tokens  # Default limit for all runs
        
        # Detect available CLI tools
        self._detect_cli_tools()
        
        # Initialize cache
        self.cache_enabled = os.getenv('POLYCLI_CACHE', 'false').lower() == 'true'
        self.cache_dir = Path(self.cwd) / '.polycache'
        if self.cache_enabled and not self.cache_dir.exists():
            self.cache_dir.mkdir(exist_ok=True)
    
    def _detect_cli_tools(self):
        """Detect which CLI tools are available."""
        self._claude_cmd = shutil.which('claude')
        self._qwen_cmd = shutil.which('qwen')
        self._codex_cmd = shutil.which('codex')

        if self.debug:
            print(f"[DEBUG] Claude CLI available: {bool(self._claude_cmd)}")
            print(f"[DEBUG] Qwen CLI available: {bool(self._qwen_cmd)}")
            print(f"[DEBUG] Codex CLI available: {bool(self._codex_cmd)}")
    
    def add_user_message(self, user_text: str, position: str = "end"):
        """
        Add a user message to the conversation.
        
        Args:
            user_text: The message content
            position: Where to add the message ("start" or "end")
        """
        self.messages.add_user_message(user_text, position)
        
        if self.debug:
            print(f"[DEBUG] Added user message. Total messages: {len(self.messages)}")
    
    def run(self, 
            prompt: str,
            model: Optional[str] = None,
            cli: Optional[str] = None,
            system_prompt: Optional[str] = None,
            ephemeral: bool = False,
            schema_cls: Optional[Type[BaseModel]] = None,
            memory_serializer: Optional[Callable[[BaseModel], str]] = None,
            max_tokens: Optional[int] = None,
            tracked: bool = False,
            use_cache: Optional[bool] = None,
            stream: bool = False,
            stream_events: bool = False,
            **kwargs):
        """
        Run a prompt with automatic backend selection and token management.
        
        Args:
            prompt: The prompt to execute
            model: Model name (e.g., "gpt-5")
            cli: Backend to use:
                - "claude-code": Use Claude CLI
                - "qwen-code": Use Qwen CLI
                - "codex": Use Codex CLI
                - "mini-swe": Use Mini-SWE Agent
                - "no-tools": Use direct API without tools
                - None: Auto-detect based on model/availability
            system_prompt: System prompt for this run
            ephemeral: If True, don't save to message history
            schema_cls: Pydantic model for structured output
            memory_serializer: Custom serializer for structured output
            max_tokens: Token limit for this run (overrides agent default)
            tracked: If True, wrap this call in a pattern for orchestration tracking
            use_cache: If True/False, override environment cache setting for this call
            stream: If True and cli="no-tools", stream tokens to session (if available)
            **kwargs: Additional backend-specific parameters
        
        Returns:
            RunResult when stream_events=False
            Generator[ClaudeEvent|RunResult] when stream_events=True
        """
        # Always use generator internally
        gen = self._run_generator(
            prompt, model, cli, system_prompt, ephemeral,
            schema_cls, memory_serializer, max_tokens,
            tracked, use_cache, stream, stream_events, **kwargs
        )
        if stream_events:
            if tracked:
                return next(gen)
            else:
                return gen  # Return generator itself
        else:
            # Consume generator and return just the RunResult
            for item in gen:
                if isinstance(item, RunResult):
                    return item
    
    def _run_generator(self,
            prompt: str,
            model: Optional[str] = None,
            cli: Optional[str] = None,
            system_prompt: Optional[str] = None,
            ephemeral: bool = False,
            schema_cls: Optional[Type[BaseModel]] = None,
            memory_serializer: Optional[Callable[[BaseModel], str]] = None,
            max_tokens: Optional[int] = None,
            tracked: bool = False,
            use_cache: Optional[bool] = None,
            stream: bool = False,
            stream_events: bool = False,
            **kwargs):
        """Internal generator that handles all execution logic."""
        # If tracked, delegate to the pattern-wrapped version
        if tracked:
            yield tracked_run(
                self, prompt,
                model=model, cli=cli, system_prompt=system_prompt,
                ephemeral=ephemeral, schema_cls=schema_cls,
                memory_serializer=memory_serializer, max_tokens=max_tokens,
                use_cache=use_cache, stream=stream, stream_events=stream_events, **kwargs
            )
            return
        
        # Check cache first (use_cache overrides environment setting)
        should_cache = use_cache if use_cache is not None else self.cache_enabled
        
        if should_cache:
            cache_key = self._cache_key(prompt, model, cli, system_prompt, ephemeral)
            cached_data = self._load_from_cache(cache_key)
            if cached_data:
                yield self._restore_cached_result(cached_data, cache_key)
                return
        
        # Determine effective token limit
        # @@@qwen-session-limit: Default 100k, matches Qwen's global limit in __init__.py
        effective_limit = max_tokens or self.max_tokens or 100000
        
        # Pre-emptive compaction check (before routing to backend)
        current_tokens = self.messages.estimate_tokens()
        if current_tokens > effective_limit * 0.8:  # 80% threshold
            if self.debug:
                print(f"[DEBUG] Pre-emptive compaction: {current_tokens} tokens > 80% of {effective_limit} limit")
            self.compact_messages(model or "gpt-5")
            current_tokens = self.messages.estimate_tokens()  # Update count
        
        # Determine which backend to use
        backend = self._determine_backend(cli, model)
        
        if self.debug:
            print(f"[DEBUG] PolyAgent routing to backend: {backend}")
        
        # Try the request with retry on token-related failures
        max_retries = 2  # Try original + 1 retry after compaction
        already_yielded = False  # Track if we already yielded from a generator
        
        for attempt in range(max_retries):
            # Route to backend
            if backend == "claude-code":
                # Use ClaudeClient
                result = ClaudeClient.run_cli(self, prompt, system_prompt, ephemeral, stream_events)
                # If it's a generator (stream_events=True), yield from it
                if hasattr(result, '__iter__'):
                    for item in result:
                        yield item
                        if isinstance(item, RunResult):
                            result = item  # Keep last RunResult for retry logic
                    already_yielded = True  # Mark that we've already yielded the result
            elif backend == "qwen-code":
                result = QwenClient.run_cli(self, prompt, model or "gpt-5", system_prompt, ephemeral)
            elif backend == "codex":
                result = CodexClient.run_cli(self, prompt, system_prompt, ephemeral)
            elif backend == "mini-swe":
                result = MiniSweClient.run_cli(self, prompt, model or "gpt-5", system_prompt, ephemeral, schema_cls, memory_serializer)
            else:  # no-tools
                result = ApiClient.run_cli(self, prompt, model or "gpt-5", system_prompt, ephemeral, schema_cls, memory_serializer, stream, **kwargs)
            
            # Check if we should retry with compaction
            if attempt == 0 and self._should_retry_with_compact(result, current_tokens, effective_limit):
                if self.debug:
                    print(f"[DEBUG] Attempting compact-and-retry due to suspected token limit issue")
                    print(f"[DEBUG] Current tokens: {current_tokens}, Limit: {effective_limit}")
                
                # Save state before compaction
                original_messages = self.messages.messages[:]
                
                try:
                    self.compact_messages(model or "gpt-5")
                    new_tokens = self.messages.estimate_tokens()
                    if self.debug:
                        print(f"[DEBUG] Compacted from {current_tokens} to {new_tokens} tokens")
                    current_tokens = new_tokens
                    # Continue to next iteration for retry
                    continue
                except Exception as e:
                    # Restore on failure
                    self.messages.messages = original_messages
                    if self.debug:
                        print(f"[DEBUG] Compaction failed, returning original error: {e}")
                    # Fall through to return original result
            
            # Save to cache if successful and caching enabled
            if should_cache and result.is_success:
                self._save_to_cache(cache_key, result, self.messages)
                # @@@ cache-tracking - Store cache info for potential rollback
                result._cache_key = cache_key
                result._cache_dir = self.cache_dir
            
            # Yield result (either success or final failure)
            if not already_yielded:
                yield result
            return
        
        # Should never reach here - if we do, it's a bug
        raise RuntimeError(
            f"Reached unexpected code path in _run_generator. "
            f"Backend: {backend}, already_yielded: {already_yielded}"
        )
    
    def _determine_backend(self, cli: Optional[str], model: Optional[str]) -> str:
        """
        Determine which backend to use.
        
        Priority:
        1. Explicit cli parameter
        2. Model-based detection
        3. Available CLI tools
        4. Default to API
        """
        # Explicit CLI specification takes precedence
        if cli:
            return cli
        
        # Model-based detection
        if model:
            model_lower = model.lower()
            if "claude" in model_lower:
                # Claude model - use Claude CLI if available
                if self._claude_cmd:
                    return "claude-code"
                else:
                    return "no-tools"
            else:
                # Non-Claude model - default to no-tools
                return "no-tools"
        
        # No model specified - use available CLI tools
        if self._claude_cmd:
            return "claude-code"
        elif self._qwen_cmd:
            return "qwen-code"
        elif self._codex_cmd:
            return "codex"
        else:
            return "no-tools"

    def save_state(self, file_path: str):
        """
        Save conversation state to a file in original raw formats.
        This preserves the source format of each message.
        
        Args:
            file_path: Path to save to (.json or .jsonl)
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Extract raw messages
        raw_messages = []
        for msg in self.messages:
            if hasattr(msg, '_raw') and msg._raw:
                raw_messages.append(msg._raw)
            else:
                # Fallback if no _raw field (shouldn't happen)
                raw_messages.append({"role": msg.role, "content": msg.content})
        
        # Write based on file extension
        if path.suffix == '.jsonl':
            # JSONL format (one message per line)
            with open(path, 'w', encoding='utf-8') as f:
                for msg in raw_messages:
                    f.write(json.dumps(msg, ensure_ascii=False) + '\n')
        else:
            # JSON array format
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(raw_messages, f, ensure_ascii=False, indent=2)
        
        if self.debug:
            print(f"[DEBUG] Saved {len(raw_messages)} messages to {path} (preserving original formats)")
    
    def load_state(self, file_path: str):
        """
        Load conversation state from a file.
        Auto-detects format.
        """
        path = Path(file_path)
        
        if not path.exists():
            if self.debug:
                print(f"[DEBUG] File not found: {path}")
            return
        
        # Load based on extension
        if path.suffix == '.jsonl':
            # Claude JSONL format - load all messages including tool interactions
            messages = []
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        messages.append(json.loads(line))
            
            # MessageList will handle the format conversion properly
            self.messages = MessageList(messages)
        
        else:
            # JSON format (Qwen or standard)
            with open(path, 'r', encoding='utf-8') as f:
                messages = json.load(f)
            
            self.messages = MessageList(messages)
        
        if self.debug:
            print(f"[DEBUG] Loaded {len(self.messages)} messages from {path}")
    
    def _encode_path(self, path_str: str) -> str:
        """Encode path for Claude session files."""
        if sys.platform == "win32" and ":" in path_str:
            drive, rest = path_str.split(":", 1)
            rest = rest.lstrip(os.path.sep)
            path_str = f"{drive}--{rest}"
        # Replace path separators with dashes, then replace underscores with dashes
        # This matches Claude CLI's own encoding behavior
        return path_str.replace(os.path.sep, '-').replace('_', '-')
    
    def _should_retry_with_compact(self, result: RunResult, token_estimate: int, limit: int) -> bool:
        """Check if we should compact and retry based on result.
        
        Args:
            result: The result from the backend
            token_estimate: Current estimated token count
            limit: Token limit
            
        Returns:
            True if we should compact and retry
        """
        # Only compact if we're using significant tokens
        if token_estimate < limit * 0.5:  # Less than 50% usage
            return False
        
        # Check if result indicates failure
        if not isinstance(result, RunResult):
            return False
        
        # Check 1: Error status
        if not result.is_success:
            return True
        
        # Check 2: Empty response (Qwen's silent failure mode)
        # This happens when Qwen fails due to token limit
        if result.raw_result and 'message' in result.raw_result:
            msg = result.raw_result.get('message', {})
            if isinstance(msg, dict) and not msg.get('content', '').strip():
                if self.debug:
                    print("[DEBUG] Empty assistant response detected with high token usage")
                return True
        
        # Check 3: Placeholder for future checks
        # Could add patterns like "context length exceeded" in error messages
        
        return False
    
    def compact_messages(self, model: str = "gpt-5"):
        """
        Compact conversation history by summarizing.
        Delegates to MessageList's compact method.
        """
        if hasattr(self.messages, 'compact'):
            self.messages = self.messages.compact(model=model, debug=self.debug)
        else:
            if self.debug:
                print("[DEBUG] MessageList doesn't support compaction")
    
    def _cache_key(self, prompt: str, model: Optional[str], cli: Optional[str], 
                   system_prompt: Optional[str], ephemeral: bool) -> str:
        """Generate cache key for a run() call."""
        key_data = {
            'prompt': prompt,
            'model': model, 
            'cli': cli,
            'system_prompt': system_prompt,
            'ephemeral': ephemeral,
            'messages_hash': self.messages.content_hash(),
        }
        return hashlib.sha256(json.dumps(key_data, sort_keys=True).encode()).hexdigest()[:16]
    
    def _load_from_cache(self, cache_key: str) -> Optional[dict]:
        """Load cached result and restore agent state."""
        if not self.cache_enabled:
            return None
            
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            if self.debug:
                print(f"[DEBUG] Cache miss: {cache_key}")
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            if self.debug:
                print(f"[DEBUG] Cache hit: {cache_key}")
            
            return cached_data
            
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] Cache load failed for {cache_key}: {e}")
            return None
    
    def _save_to_cache(self, cache_key: str, result: RunResult, post_messages: MessageList):
        """Save result and post-run agent state to cache."""
        if not self.cache_enabled:
            return
            
        try:
            import pickle
            import time
            
            cache_data = {
                'result': pickle.dumps(result).hex(),  # Serialize to hex string for JSON
                'post_messages': post_messages.to_raw_list(),  # Save raw message data
                'timestamp': time.time()
            }
            
            cache_file = self.cache_dir / f"{cache_key}.json"
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
            if self.debug:
                print(f"[DEBUG] Cached result: {cache_key}")
                
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] Cache save failed for {cache_key}: {e}")
    
    def _restore_cached_result(self, cached_data: dict, cache_key: str) -> RunResult:
        """Restore agent state and return cached result."""
        import pickle
        
        try:
            # Restore agent message state
            raw_messages = cached_data.get('post_messages', [])
            self.messages = MessageList(raw_messages)
            
            # Restore result object
            result_hex = cached_data.get('result', '')
            result_bytes = bytes.fromhex(result_hex)
            result = pickle.loads(result_bytes)
            
            # @@@ from-cache-flag - Mark this result as coming from cache
            result.from_cache = True
            # Store cache info so this result can be invalidated if needed
            result._cache_key = cache_key
            result._cache_dir = self.cache_dir
            
            if self.debug:
                print(f"[DEBUG] Restored {len(raw_messages)} messages from cache")
                
            return result
            
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] Cache restore failed: {e}")
            # Return empty result on failure
            return RunResult({"status": "error", "message": "Cache restore failed"}, from_cache=False)
