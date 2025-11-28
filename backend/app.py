"""
FastAPI Application

Main application entry point with HTTP and WebSocket routes.
Most data flows over WebSocket; HTTP routes are minimal.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import json

from db_connector import get_session, init_db
from websocket_manager import websocket_manager
from repair_service import RepairService

app = FastAPI(title="Repair Tracker 2")

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    # Note: init_db() is typically not called in production
    # since the database schema is frozen with production data
    pass


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {"status": "ok", "service": "repair-tracker-2"}


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# HTTP API Routes (minimal - most data flows over WebSocket)

@app.get("/api/assignees")
async def get_assignees(session: Session = Depends(get_session)):
    """Get all assignees."""
    service = RepairService(session)
    return service.get_all_assignees()


@app.get("/api/statuses")
async def get_statuses(session: Session = Depends(get_session)):
    """Get all statuses."""
    service = RepairService(session)
    return service.get_all_statuses()


@app.get("/api/models")
async def get_unit_models(session: Session = Depends(get_session)):
    """Get all unit models."""
    service = RepairService(session)
    return service.get_all_unit_models()


@app.get("/api/orders")
async def get_orders(session: Session = Depends(get_session)):
    """Get all repair orders (metadata)."""
    service = RepairService(session)
    return service.get_all_orders()


@app.get("/api/orders/{order_id}")
async def get_order(order_id: int, session: Session = Depends(get_session)):
    """Get a specific repair order with units."""
    service = RepairService(session)
    order = service.get_order_by_id(order_id)
    if not order:
        return {"error": "Order not found"}, 404
    return order


# WebSocket endpoint

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates.

    Expected message format from client:
    {
        "type": "subscribe",
        "channels": ["main", "order:123"]
    }

    Server sends initial data after subscription, then sends updates
    as they occur via the event bus.
    """
    await websocket_manager.connect(websocket)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)

            message_type = message.get("type")

            if message_type == "subscribe":
                channels = message.get("channels", [])
                await websocket_manager.subscribe_to_channels(
                    websocket,
                    channels
                )

                # Send initial data for subscribed channels
                # This would typically fetch current state and send it
                # Placeholder for now
                await websocket.send_json({
                    "type": "subscribed",
                    "channels": channels,
                    "message": "Subscribed successfully"
                })

            elif message_type == "ping":
                # Keepalive ping/pong
                await websocket.send_json({"type": "pong"})

            else:
                # Unknown message type
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                })

    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket_manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
