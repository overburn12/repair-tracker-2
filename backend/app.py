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
from events import event_bus
import websocket_handlers
import request_handlers

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


@app.get("/api/get_holidays")
async def get_holidays():
    """Get list of federal holidays for 2025-2026."""
    holidays = [
        # 2025
        "2025-01-01",  # New Year's Day
        "2025-01-20",  # Martin Luther King Jr. Day
        "2025-02-17",  # Presidents' Day
        "2025-05-26",  # Memorial Day
        "2025-06-19",  # Juneteenth
        "2025-07-04",  # Independence Day
        "2025-09-01",  # Labor Day
        "2025-10-13",  # Columbus Day
        "2025-11-11",  # Veterans Day
        "2025-11-27",  # Thanksgiving
        "2025-12-25",  # Christmas
        # 2026
        "2026-01-01",  # New Year's Day
        "2026-01-19",  # Martin Luther King Jr. Day
        "2026-02-16",  # Presidents' Day
        "2026-05-25",  # Memorial Day
        "2026-06-19",  # Juneteenth
        "2026-07-03",  # Independence Day (observed)
        "2026-09-07",  # Labor Day
        "2026-10-12",  # Columbus Day
        "2026-11-11",  # Veterans Day
        "2026-11-26",  # Thanksgiving
        "2026-12-25",  # Christmas
    ]
    return {"holidays": holidays}


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
    WebSocket endpoint for real-time bidirectional updates.

    On connect: Sends websocket_id to client

    Client->Server messages:
    - subscribe: {"type": "subscribe", "channels": [...]}
    - update: {"channel": "...", "type": "update", "data": [...]}
    - delete: {"channel": "...", "type": "delete", "data": [...keys...]}
    - ping: {"type": "ping"}

    Server->Client: Formatted messages from event bus
    """
    # Connect and get websocket_id
    websocket_id = await websocket_manager.connect(websocket)

    # Send websocket_id to client
    await websocket.send_json({
        "type": "connected",
        "websocket_id": websocket_id
    })

    # Get database session for this connection
    session_gen = get_session()
    session = next(session_gen)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)

            message_type = message.get("type")

            if message_type == "subscribe":
                # Handle channel subscription
                channels = message.get("channels", [])
                await websocket_manager.subscribe_to_channels(
                    websocket,
                    channels
                )

                # Send initial data for each channel
                for channel in channels:
                    initial_data = (
                        await websocket_handlers.get_initial_data_for_channel(
                            channel,
                            session
                        )
                    )
                    if initial_data:
                        await websocket.send_json(initial_data)

            elif message_type == "update":
                # Handle update from frontend
                error = await request_handlers.handle_update_request(
                    message,
                    websocket_id,
                    session
                )
                if error:
                    # Send error message via __messages__ channel
                    error_msg = websocket_handlers.format_error_message(
                        websocket_id,
                        error
                    )
                    await event_bus.publish(
                        event_bus.get_messages_channel(),
                        error_msg
                    )

            elif message_type == "delete":
                # Handle delete from frontend
                error = await request_handlers.handle_delete_request(
                    message,
                    websocket_id,
                    session
                )
                if error:
                    # Send error message via __messages__ channel
                    error_msg = websocket_handlers.format_error_message(
                        websocket_id,
                        error
                    )
                    await event_bus.publish(
                        event_bus.get_messages_channel(),
                        error_msg
                    )

            elif message_type == "ping":
                # Keepalive ping/pong
                await websocket.send_json({"type": "pong"})

            else:
                # Unknown message type
                error_msg = websocket_handlers.format_error_message(
                    websocket_id,
                    f"Unknown message type: {message_type}"
                )
                await websocket.send_json(error_msg)

    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket_manager.disconnect(websocket)
    finally:
        # Clean up session
        try:
            session.close()
        except Exception:
            pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
