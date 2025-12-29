"""FastAPI application for AI Counsel web interface."""

import asyncio
import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from ..core.base_agent import AgentRole
from ..core.config import Config
from ..counsel import AICounsel

# Paths
WEB_DIR = Path(__file__).parent
TEMPLATES_DIR = WEB_DIR / "templates"
STATIC_DIR = WEB_DIR / "static"


def create_app(config: Optional[Config] = None) -> FastAPI:
    """Create the FastAPI application."""
    app = FastAPI(
        title="AI Counsel",
        description="A council of specialized AI agents for building applications",
        version="0.1.0",
    )

    # Mount static files
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    # Templates
    templates = Jinja2Templates(directory=TEMPLATES_DIR)

    # Store config and counsel instance
    app.state.config = config
    app.state.counsel = None

    @app.on_event("startup")
    async def startup():
        """Initialize the counsel on startup."""
        if app.state.config is None:
            app.state.config = Config.from_env()
        app.state.counsel = AICounsel(app.state.config)

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        """Render the main chat interface."""
        agents = [
            {"role": role.value, "name": role.value.title()}
            for role in AgentRole
            if role != AgentRole.ORCHESTRATOR
        ]
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "agents": agents},
        )

    @app.get("/api/agents")
    async def get_agents():
        """Get list of available agents."""
        counsel: AICounsel = app.state.counsel
        return {"agents": counsel.list_agents()}

    @app.websocket("/ws/chat")
    async def websocket_chat(websocket: WebSocket):
        """WebSocket endpoint for chat interactions."""
        await websocket.accept()
        counsel: AICounsel = app.state.counsel

        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)

                task = message.get("task", "")
                selected_agents = message.get("agents", [])

                if not task:
                    await websocket.send_json({
                        "type": "error",
                        "content": "Please enter a task or question.",
                    })
                    continue

                # Send acknowledgment
                await websocket.send_json({
                    "type": "status",
                    "content": "Analyzing your request...",
                })

                # Parse agent selection
                agent_roles = None
                if selected_agents:
                    agent_roles = []
                    for agent_name in selected_agents:
                        try:
                            agent_roles.append(AgentRole(agent_name.lower()))
                        except ValueError:
                            pass

                try:
                    # Get analysis first
                    analysis = await counsel.orchestrator.analyze_task(task)

                    agents_to_consult = agent_roles or [
                        AgentRole(role.lower())
                        for role in analysis.get("agents_needed", ["architect", "developer"])
                        if role.lower() in [r.value for r in AgentRole]
                    ]

                    await websocket.send_json({
                        "type": "analysis",
                        "content": analysis.get("analysis", ""),
                        "agents": [a.value for a in agents_to_consult],
                    })

                    # Consult the counsel
                    session = await counsel.consult(
                        task=task,
                        agents=agent_roles,
                    )

                    # Send each agent's response
                    for response in session.responses:
                        await websocket.send_json({
                            "type": "agent_response",
                            "agent": response.agent_role.value,
                            "content": response.content,
                        })
                        # Small delay for better UX
                        await asyncio.sleep(0.1)

                    # Send synthesis if available
                    if session.synthesis:
                        await websocket.send_json({
                            "type": "synthesis",
                            "content": session.synthesis,
                        })

                    # Send completion signal
                    await websocket.send_json({
                        "type": "complete",
                        "content": "Consultation complete.",
                    })

                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "content": f"Error during consultation: {str(e)}",
                    })

        except WebSocketDisconnect:
            pass
        except Exception as e:
            try:
                await websocket.send_json({
                    "type": "error",
                    "content": f"Connection error: {str(e)}",
                })
            except Exception:
                pass

    return app


def run_server(
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = False,
    config: Optional[Config] = None,
):
    """Run the web server."""
    import uvicorn

    # Create app with config
    app = create_app(config)

    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload,
    )
