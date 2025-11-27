import os
import grpc
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis import Redis
from google.cloud.tasks_v2 import CloudTasksClient
from google.cloud.tasks_v2.services.cloud_tasks.transports import (
    CloudTasksGrpcTransport,
)

from app.routes import health, api
from app.services import scrap
from app.exceptions import setup_exception_handlers

import sentry_sdk

logger = logging.getLogger(__name__)


sentry_sdk.init(
    dsn=os.getenv(
        "SENTRY_DSN",
    )
    or "https://1efc1f4c5af433491b7c5d7413a594f4@o1423748.ingest.us.sentry.io/4509553793564672",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan: startup and shutdown events"""
    # Startup: Initialize dependencies
    logger.info("Starting up: Initializing dependencies...")

    # Redis
    redis_client = Redis(
        host=os.getenv("REDIS_HOST_URL"),
        port=os.getenv("REDIS_PORT"),
        db=os.getenv("REDIS_DB", 0),
        decode_responses=True,
    )

    # Cloud Tasks
    cloud_task_host = os.getenv("CLOUD_TASK_HOST_URL")
    cloud_task_port = os.getenv("CLOUD_TASK_PORT")

    if cloud_task_host and cloud_task_port:
        channel = grpc.insecure_channel(f"{cloud_task_host}:{cloud_task_port}")
        transport = CloudTasksGrpcTransport(channel=channel)
        cloud_tasks_client = CloudTasksClient(transport=transport)
    else:
        # For local dev without cloud tasks emulator, use a mock
        from unittest.mock import MagicMock
        cloud_tasks_client = MagicMock()
        logger.warning("Cloud Tasks not configured. Using mock client.")

    # Initialize services with clients
    scrap.init_clients(redis_client, cloud_tasks_client)
    logger.info("Dependencies initialized successfully")

    yield  # Application runs here

    # Shutdown: Cleanup (if needed)
    logger.info("Shutting down: Cleaning up resources...")
    # Add any cleanup logic here if needed
    logger.info("Shutdown complete")


# Create FastAPI app with lifespan
app = FastAPI(
    title="Scrap LLM API",
    description="API for web scraping with LLM capabilities",
    version="1.0.0",
    lifespan=lifespan,
    debug=os.getenv("DEBUG", "false").lower() == "true",
)

# Configure exception handlers
setup_exception_handlers(app)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://10.98.105.143:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(health.router)
app.include_router(api.router)


def run():
    """Entry point for the poetry script to run the FastAPI server"""
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
