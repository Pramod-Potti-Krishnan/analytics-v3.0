"""
WebSocket server for Analytics Microservice v3.
"""

import json
import logging
import uuid
from typing import Dict, Set
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
import uvicorn

from .agent import process_analytics_request
from .dependencies import AnalyticsDependencies
from .settings import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=settings.log_level)

# Store active WebSocket connections
connections: Dict[str, WebSocket] = {}
dependencies_map: Dict[str, AnalyticsDependencies] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Analytics Microservice v3")
    yield
    # Cleanup on shutdown
    logger.info("Shutting down Analytics Microservice v3")
    for dep in dependencies_map.values():
        await dep.cleanup()
    connections.clear()
    dependencies_map.clear()


app = FastAPI(
    title="Analytics Microservice v3",
    description="WebSocket-based analytics chart generation service",
    version="3.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Analytics Microservice v3",
        "status": "running",
        "websocket_endpoint": "/ws",
        "health_endpoint": "/health",
        "active_connections": len(connections),
        "max_connections": settings.max_concurrent_connections
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.railway_environment,
        "active_connections": len(connections),
        "max_connections": settings.max_concurrent_connections
    }


async def send_websocket_message(websocket: WebSocket, message: Dict):
    """Send JSON message via WebSocket."""
    try:
        await websocket.send_json(message)
    except Exception as e:
        logger.error(f"Failed to send WebSocket message: {e}")


async def handle_progress_update(update_data: Dict):
    """Handle progress update callback from agent."""
    websocket_id = update_data.get("websocket_id")
    if websocket_id in connections:
        websocket = connections[websocket_id]
        await send_websocket_message(websocket, {
            "type": "progress",
            **update_data
        })


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for analytics requests.
    
    Message Protocol:
    Request:
    {
        "type": "analytics_request",
        "request_id": "unique_id",
        "content": "description of analytics needed",
        "title": "optional chart title",
        "data": optional user data array,
        "theme": "optional theme name",
        "chart_type": "optional preferred chart type",
        "options": {
            "use_synthetic_data": boolean,
            "enhance_labels": boolean,
            "output_format": "png|svg|html"
        }
    }
    
    Response:
    {
        "type": "analytics_response",
        "request_id": "matching_request_id",
        "success": boolean,
        "chart": "base64 encoded image or svg string",
        "data": structured chart data,
        "metadata": {
            "chart_type": "actual chart type used",
            "generation_method": "method used",
            "data_source": "user|synthetic",
            "generation_time_ms": number,
            "insights": ["array of insights"]
        },
        "error": "error message if failed"
    }
    
    Progress Updates:
    {
        "type": "progress",
        "request_id": "matching_request_id",
        "stage": "initialization|data_processing|chart_rendering|completion",
        "progress": 0-100,
        "message": "current activity description"
    }
    """
    connection_id = str(uuid.uuid4())
    
    # Accept connection
    await websocket.accept()
    logger.info(f"WebSocket connection established: {connection_id}")
    
    # Create dependencies for this connection
    deps = AnalyticsDependencies.from_settings(
        settings,
        websocket_id=connection_id,
        progress_callback=handle_progress_update
    )
    
    # Check if we can accept this connection
    if not deps.add_connection(connection_id):
        await send_websocket_message(websocket, {
            "type": "error",
            "error": "Maximum connections reached",
            "code": 1013
        })
        await websocket.close(code=1013, reason="Max connections reached")
        return
    
    # Store connection and dependencies
    connections[connection_id] = websocket
    dependencies_map[connection_id] = deps
    
    # Send welcome message
    await send_websocket_message(websocket, {
        "type": "connection",
        "connection_id": connection_id,
        "status": "connected",
        "message": "Analytics Microservice v3 ready"
    })
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                request_type = message.get("type")
                request_id = message.get("request_id", str(uuid.uuid4()))
                
                if request_type == "analytics_request":
                    # Update dependencies with request ID
                    deps.chart_request_id = request_id
                    deps.generation_start_time = datetime.utcnow()
                    
                    # Process analytics request
                    logger.info(f"Processing analytics request {request_id} for connection {connection_id}")
                    
                    # Prepare request data
                    request_data = {
                        "content": message.get("content", ""),
                        "title": message.get("title"),
                        "data": message.get("data"),
                        "chart_type": message.get("chart_type", "bar_vertical"),
                        "theme": message.get("theme", "default"),
                        "websocket_id": connection_id,
                        "request_id": request_id,
                        "progress_callback": handle_progress_update
                    }
                    
                    # Add options if provided
                    options = message.get("options", {})
                    request_data.update(options)
                    
                    # Process request
                    result = await process_analytics_request(request_data)
                    
                    # Calculate generation time
                    generation_time = (datetime.utcnow() - deps.generation_start_time).total_seconds() * 1000
                    
                    # Send response
                    response = {
                        "type": "analytics_response",
                        "request_id": request_id,
                        "success": result.get("success", False),
                        "chart": result.get("chart"),
                        "metadata": {
                            **result.get("metadata", {}),
                            "generation_time_ms": generation_time,
                            "data_source": "synthetic" if not message.get("data") else "user"
                        }
                    }
                    
                    if not result.get("success"):
                        response["error"] = result.get("error", "Unknown error")
                    
                    await send_websocket_message(websocket, response)
                    
                elif request_type == "ping":
                    # Handle ping/pong for connection keep-alive
                    await send_websocket_message(websocket, {
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
                else:
                    # Unknown message type
                    await send_websocket_message(websocket, {
                        "type": "error",
                        "request_id": request_id,
                        "error": f"Unknown message type: {request_type}"
                    })
                    
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON received: {e}")
                await send_websocket_message(websocket, {
                    "type": "error",
                    "error": "Invalid JSON format"
                })
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await send_websocket_message(websocket, {
                    "type": "error",
                    "error": str(e)
                })
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket connection closed: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket error for {connection_id}: {e}")
    finally:
        # Cleanup
        if connection_id in connections:
            del connections[connection_id]
        if connection_id in dependencies_map:
            deps = dependencies_map[connection_id]
            deps.remove_connection(connection_id)
            await deps.cleanup()
            del dependencies_map[connection_id]
        logger.info(f"Connection {connection_id} cleaned up")


def run_server():
    """Run the WebSocket server."""
    import os
    # Try to get port from environment variable first, then settings
    port = int(os.environ.get('PORT', os.environ.get('WEBSOCKET_PORT', settings.websocket_port)))
    
    logger.info(f"Starting WebSocket server on port {port}")
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level=settings.log_level.lower()
        )
    except OSError as e:
        if "address already in use" in str(e).lower():
            logger.error(f"Port {port} is already in use. Try:")
            logger.error(f"  1. Kill the process: lsof -i :{port} then kill -9 <PID>")
            logger.error(f"  2. Use a different port: WEBSOCKET_PORT=8081 python main.py")
            logger.error(f"  3. Check for other running instances: ps aux | grep main.py")
            raise
        else:
            raise


if __name__ == "__main__":
    run_server()