"""FastAPI application for AI Counsel web interface."""

import asyncio
import json
import logging
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

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

    @app.get("/health")
    async def health_check():
        """Health check endpoint for Cloud Run."""
        return {"status": "healthy", "service": "ai-counsel"}

    @app.get("/ready")
    async def readiness_check():
        """Readiness check - verifies counsel is initialized."""
        if app.state.counsel is None:
            return {"status": "not_ready"}, 503
        return {"status": "ready"}

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
        logger.info("WebSocket connection established")

        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                logger.info(f"Received message: {data[:100]}...")
                message = json.loads(data)

                task = message.get("task", "")
                selected_agents = message.get("agents", [])
                logger.info(f"Task: {task[:50]}... | Agents: {selected_agents}")

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
                logger.info("Sent status acknowledgment")

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
                    logger.info("Starting task analysis...")
                    analysis = await counsel.orchestrator.analyze_task(task)
                    logger.info(f"Analysis complete: {analysis}")

                    agents_to_consult = agent_roles or [
                        AgentRole(role.lower())
                        for role in analysis.get("agents_needed", ["architect", "developer"])
                        if role.lower() in [r.value for r in AgentRole]
                    ]
                    logger.info(f"Agents to consult: {agents_to_consult}")

                    await websocket.send_json({
                        "type": "analysis",
                        "content": analysis.get("analysis", ""),
                        "agents": [a.value for a in agents_to_consult],
                    })

                    # Consult the counsel
                    logger.info("Starting consultation...")
                    session = await counsel.consult(
                        task=task,
                        agents=agent_roles,
                    )
                    logger.info(f"Consultation complete. Got {len(session.responses)} responses")

                    # Send each agent's response
                    for response in session.responses:
                        logger.info(f"Sending response from {response.agent_role.value}")
                        await websocket.send_json({
                            "type": "agent_response",
                            "agent": response.agent_role.value,
                            "content": response.content,
                        })
                        # Small delay for better UX
                        await asyncio.sleep(0.1)

                    # Send synthesis if available
                    if session.synthesis:
                        logger.info("Sending synthesis")
                        await websocket.send_json({
                            "type": "synthesis",
                            "content": session.synthesis,
                        })

                    # Send completion signal
                    await websocket.send_json({
                        "type": "complete",
                        "content": "Consultation complete.",
                    })
                    logger.info("Consultation flow complete")

                except Exception as e:
                    logger.error(f"Error during consultation: {str(e)}", exc_info=True)
                    await websocket.send_json({
                        "type": "error",
                        "content": f"Error during consultation: {str(e)}",
                    })

        except WebSocketDisconnect:
            logger.info("WebSocket disconnected")
        except Exception as e:
            logger.error(f"WebSocket error: {str(e)}", exc_info=True)
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
