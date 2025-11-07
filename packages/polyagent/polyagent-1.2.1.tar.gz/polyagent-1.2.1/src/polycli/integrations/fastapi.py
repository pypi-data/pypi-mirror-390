"""
FastAPI integration for PolyCLI session registry.

This module allows mounting PolyCLI session control panel onto a FastAPI application,
enabling hot reloading, async support, and integration with custom routes.

Example:
    from fastapi import FastAPI
    from polycli.orchestration import get_registry
    from polycli.integrations.fastapi import mount_control_panel
    import uvicorn

    app = FastAPI()

    # Your custom routes
    @app.get("/health")
    def health():
        return {"status": "ok"}

    # Mount PolyCLI control panel
    registry = get_registry()
    mount_control_panel(app, registry, prefix="/polycli")

    if __name__ == "__main__":
        uvicorn.run(app, port=8765, reload=True)
"""

from pathlib import Path
from typing import Optional, Callable

try:
    from fastapi import FastAPI, HTTPException, Query, Header
    from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
    from starlette.requests import Request
except ImportError:
    raise ImportError(
        "FastAPI is not installed. Install with: pip install 'polyagent[fastapi]'"
    )

from ..orchestration.session_registry import SessionRegistry
from ..orchestration.orchestration import SessionMonitor


def mount_control_panel(
    app: FastAPI,
    registry: SessionRegistry,
    prefix: str = "/polycli",
    auth_callback: Optional[Callable[[str], Optional[dict]]] = None
):
    """
    Mount PolyCLI session control panel routes onto a FastAPI application.

    Args:
        app: FastAPI application instance
        registry: SessionRegistry instance (from get_registry())
        prefix: URL prefix for all PolyCLI routes (default: "/polycli")
        auth_callback: Optional authentication callback function that takes a JWT token
                      and returns user data dict (with 'user_id' key) or None if invalid.
                      If provided, /api/trigger-sync will validate Authorization header
                      and inject user_id into params.

    Example:
        app = FastAPI()
        registry = get_registry()

        # Without auth:
        mount_control_panel(app, registry, prefix="/polycli")

        # With auth:
        def verify_token(token: str) -> Optional[dict]:
            # Your JWT validation logic
            return {"user_id": 123, "email": "user@example.com"}

        mount_control_panel(app, registry, prefix="/polycli", auth_callback=verify_token)
    """

    # Root: serve control panel HTML
    @app.get(f"{prefix}/", response_class=HTMLResponse)
    @app.get(f"{prefix}", response_class=HTMLResponse, include_in_schema=False)
    async def serve_control_panel_ui():
        """Serve the main control panel UI"""
        ui_file = Path(__file__).parent.parent / "ui" / "control_panel.html"
        if not ui_file.exists():
            raise HTTPException(status_code=404, detail="Control panel UI file not found")

        with open(ui_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())

    # API: List registered sessions
    @app.get(f"{prefix}/api/sessions")
    async def list_sessions():
        """Get all registered session definitions"""
        return registry.list_registered_sessions()

    # API: List running sessions (paginated)
    @app.get(f"{prefix}/api/running")
    async def list_running(
        page: int = Query(1, ge=1, description="Page number (1-indexed)"),
        limit: int = Query(20, ge=1, le=100, description="Items per page")
    ):
        """Get running sessions with pagination"""
        return registry.list_running_sessions(page, limit)

    # API: Get specific session status
    @app.get(f"{prefix}/api/status/{{exec_id}}")
    async def get_status(exec_id: str):
        """Get detailed status of a specific session"""
        status = registry.get_session_status(exec_id)
        if status is None:
            raise HTTPException(status_code=404, detail="Session not found")
        return status

    # API: Trigger a session
    @app.post(f"{prefix}/api/trigger")
    async def trigger_session(data: dict):
        """Trigger a new session execution"""
        try:
            session_id = data["session_id"]
            params = data.get("params", {})
            exec_id = registry.trigger_session(session_id, params)
            return {"success": True, "exec_id": exec_id}
        except KeyError as e:
            raise HTTPException(status_code=400, detail=f"Missing required field: {e}")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            return {"success": False, "error": str(e)}

    # API: Trigger a session synchronously (wait for completion)
    @app.post(f"{prefix}/api/trigger-sync")
    async def trigger_session_sync(
        data: dict,
        authorization: Optional[str] = Header(None)
    ):
        """
        Trigger a session and wait for completion (synchronous).

        Request body:
        - session_id: Session definition ID (required)
        - params: Parameter values dict (optional, default: {})
        - timeout: Timeout in seconds (optional, default: 60)

        Headers:
        - Authorization: Bearer <token> (optional, used if auth_callback provided)

        Returns full status including result when session completes.
        Returns 408 Request Timeout if session exceeds timeout.
        Returns 401 Unauthorized if auth_callback provided and token is invalid.
        """
        try:
            session_id = data["session_id"]
            params = data.get("params", {})
            timeout = data.get("timeout", 60.0)

            # @@@ Auth: If auth_callback provided, validate token and inject user_id
            if auth_callback:
                if not authorization:
                    raise HTTPException(status_code=401, detail="Authorization header required")

                # Extract token (remove "Bearer " prefix if present)
                token = authorization.replace('Bearer ', '').replace('bearer ', '')

                # Validate token
                user_data = auth_callback(token)
                if not user_data or 'user_id' not in user_data:
                    raise HTTPException(status_code=401, detail="Invalid or expired token")

                # Inject user_id into params
                params['user_id'] = user_data['user_id']
                print(f"[PolyCLI Auth] Authenticated user {user_data['user_id']} for session {session_id}")

            # Run in thread pool to avoid blocking event loop
            import asyncio
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                registry.trigger_session_sync,
                session_id,
                params,
                timeout
            )
            return result
        except TimeoutError as e:
            raise HTTPException(status_code=408, detail=str(e))
        except KeyError as e:
            raise HTTPException(status_code=400, detail=f"Missing required field: {e}")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            return {"success": False, "error": str(e)}

    # API: Stop/delete a session
    @app.post(f"{prefix}/api/stop")
    async def stop_session(data: dict):
        """Stop a session (running or completed)"""
        try:
            exec_id = data["exec_id"]
            success = registry.stop_session(exec_id)
            return {"success": success}
        except KeyError:
            raise HTTPException(status_code=400, detail="Missing exec_id")

    # API: Cancel a running session
    @app.post(f"{prefix}/api/cancel")
    async def cancel_session(data: dict):
        """Force cancel a running session"""
        try:
            exec_id = data["exec_id"]
            success = registry.cancel_session(exec_id)
            return {"success": success}
        except KeyError:
            raise HTTPException(status_code=400, detail="Missing exec_id")

    # Session monitoring routes (delegate to SessionMonitor)
    @app.get(f"{prefix}/session/{{exec_id}}/", response_class=HTMLResponse, include_in_schema=False)
    @app.get(f"{prefix}/session/{{exec_id}}", response_class=HTMLResponse, include_in_schema=False)
    async def session_monitor_ui(exec_id: str):
        """Serve monitoring UI for a specific session"""
        with registry._lock:
            session_info = registry.running_sessions.get(exec_id)

        if not session_info or not session_info.get("session"):
            raise HTTPException(status_code=404, detail="Session not found")

        monitor = SessionMonitor(session_info["session"])
        base_path = f"{prefix}/session/{exec_id}"
        status, ctype, data = monitor.handle_monitor_ui(base_path)

        if status == 200:
            return HTMLResponse(content=data.decode("utf-8"))
        else:
            raise HTTPException(status_code=status)

    @app.get(f"{prefix}/session/{{exec_id}}/static/{{path:path}}")
    async def session_static(exec_id: str, path: str):
        """Serve static assets for session monitoring"""
        with registry._lock:
            session_info = registry.running_sessions.get(exec_id)

        if not session_info or not session_info.get("session"):
            raise HTTPException(status_code=404, detail="Session not found")

        monitor = SessionMonitor(session_info["session"])
        status, ctype, data = monitor.handle_static(f"/static/{path}")

        if status == 200:
            return HTMLResponse(content=data.decode("utf-8"), media_type=ctype)
        else:
            raise HTTPException(status_code=status)

    @app.get(f"{prefix}/session/{{exec_id}}/records")
    async def session_records(exec_id: str):
        """Get execution records for a session"""
        with registry._lock:
            session_info = registry.running_sessions.get(exec_id)

        if not session_info or not session_info.get("session"):
            raise HTTPException(status_code=404, detail="Session not found")

        monitor = SessionMonitor(session_info["session"])
        return monitor.handle_records()

    @app.get(f"{prefix}/session/{{exec_id}}/events")
    async def session_events(exec_id: str):
        """Server-Sent Events stream for session monitoring"""
        with registry._lock:
            session_info = registry.running_sessions.get(exec_id)

        if not session_info or not session_info.get("session"):
            raise HTTPException(status_code=404, detail="Session not found")

        monitor = SessionMonitor(session_info["session"])

        def event_generator():
            """Generator for SSE events"""
            buffer = []

            def write_fn(data):
                if isinstance(data, bytes):
                    buffer.append(data)
                else:
                    buffer.append(data.encode("utf-8"))

            def flush_fn():
                pass  # No-op for SSE

            # Use monitor's SSE handler
            monitor.handle_sse_client(write_fn, flush_fn)

            # Yield buffered data
            for chunk in buffer:
                yield chunk

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
        )

    @app.post(f"{prefix}/session/{{exec_id}}/pause")
    async def session_pause(exec_id: str):
        """Pause a running session"""
        with registry._lock:
            session_info = registry.running_sessions.get(exec_id)

        if not session_info or not session_info.get("session"):
            raise HTTPException(status_code=404, detail="Session not found")

        monitor = SessionMonitor(session_info["session"])
        return monitor.handle_pause()

    @app.post(f"{prefix}/session/{{exec_id}}/resume")
    async def session_resume(exec_id: str):
        """Resume a paused session"""
        with registry._lock:
            session_info = registry.running_sessions.get(exec_id)

        if not session_info or not session_info.get("session"):
            raise HTTPException(status_code=404, detail="Session not found")

        monitor = SessionMonitor(session_info["session"])
        return monitor.handle_resume()

    @app.post(f"{prefix}/session/{{exec_id}}/inject")
    async def session_inject(exec_id: str, data: dict):
        """Inject a message into a running session"""
        with registry._lock:
            session_info = registry.running_sessions.get(exec_id)

        if not session_info or not session_info.get("session"):
            raise HTTPException(status_code=404, detail="Session not found")

        monitor = SessionMonitor(session_info["session"])
        agent_id = data.get("agent_id", "unnamed")
        text = data.get("text", "")
        return monitor.handle_inject(agent_id, text)

    print(f"[FastAPI] PolyCLI control panel mounted at {prefix}/")
    print(f"[FastAPI] API docs available at /docs")
