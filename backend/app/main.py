import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import EXECUTION_MODE
from backend.app.routes.api_routes import router as api_router
from backend.app.services.state_manager import state_manager
from backend.app.models.schemas import HealthCheckResponse
from modules.simulation.simulation_engine import simulation_engine
from carla.carla_client_wrapper import carla_wrapper
from ai_worker.worker import ai_worker
from camera_monitoring_service import monitoring_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("AI-Driver-Monitoring-Backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown application lifecycle events."""
    logger.info(f"Initializing AI Driver Monitoring Backend (Mode: {EXECUTION_MODE.upper()})...")
    # Start default simulation tick loop & AI GPU worker
    simulation_engine.start()
    ai_worker.start()
    monitoring_service.start()
    yield
    logger.info("Shutting down AI Driver Monitoring Backend...")
    monitoring_service.stop()
    ai_worker.stop()
    simulation_engine.stop()


app = FastAPI(
    title="AI-Based Driver Monitoring and Automated Emergency Response System",
    description="College Major Project Backend API & Cloud GPU / CARLA Integration",
    version="2.0.0",
    lifespan=lifespan
)

# Allow CORS for React Frontend (running on localhost, custom domain, or cloud IP)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include REST API endpoints
app.include_router(api_router)


@app.get("/")
def read_root():
    return {
        "system": "AI-Based Driver Monitoring and Automated Emergency Response System",
        "version": "2.0.0",
        "execution_mode": EXECUTION_MODE,
        "status": "ONLINE",
        "docs": "/docs",
        "ws": "/ws/simulation"
    }


@app.get("/health", response_model=HealthCheckResponse)
def health_check():
    """Real system health endpoint evaluating actual component states."""
    state = state_manager.get_state()
    return HealthCheckResponse(
        backend=True,
        carla=state.carla_connected,
        gpu=state.cuda_available,
        ai_worker=ai_worker.is_running,
        camera=state.camera_connected,
        execution_mode=state.execution_mode
    )


@app.websocket("/ws")
@app.websocket("/ws/simulation")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    """High-frequency (10Hz) WebSocket telemetry broadcasting endpoint."""
    await websocket.accept()
    logger.info("WebSocket client connected to telemetry feed.")
    try:
        while True:
            state_data = state_manager.get_dict()
            await websocket.send_json(state_data)
            await asyncio.sleep(0.1)  # 10Hz broadcast
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected.")
    except Exception as e:
        logger.error(f"WebSocket telemetry error: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
