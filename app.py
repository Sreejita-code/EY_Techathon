# app.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import base64
from datetime import datetime
from typing import List

from database import (
    log_telematics, create_appointment, log_diagnosis,
    get_recent_alerts, get_dashboard_stats, get_customer_by_vehicle
)
# Added text_to_speech to imports
from agents import diagnose_vehicle, generate_voice_script, create_manufacturing_alert, text_to_speech

app = FastAPI(title="AgentX MVP")

# CORS for dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active connections for real-time updates
active_connections: List[WebSocket] = []

# Models
class AppointmentRequest(BaseModel):
    vehicle_id: str
    customer_name: str
    slot_time: str

# ==================== WebSocket: Vehicle Telematics ====================
@app.websocket("/ws/vehicle/{vehicle_id}")
async def vehicle_stream(websocket: WebSocket, vehicle_id: str):
    """Real-time telematics data stream"""
    await websocket.accept()
    active_connections.append(websocket)
    print(f"✅ Vehicle {vehicle_id} connected")
    
    try:
        while True:
            # Receive sensor data
            data = await websocket.receive_text()
            sensor_data = json.loads(data)
            sensor_data["vehicle_id"] = vehicle_id
            sensor_data["timestamp"] = datetime.utcnow().isoformat()
            
            # Save to database
            log_telematics(sensor_data)
            
            # Run diagnosis
            diagnosis = diagnose_vehicle(sensor_data)
            
            # If critical issue detected
            if diagnosis["status"] in ["CRITICAL", "WARNING"]:
                print(f"⚠️  ALERT: {vehicle_id} - {diagnosis['status']}")
                
                # Log diagnosis
                log_diagnosis({
                    "vehicle_id": vehicle_id,
                    "diagnosis": diagnosis,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                # Get customer info
                customer = get_customer_by_vehicle(vehicle_id)
                
                # Generate voice script
                script = generate_voice_script(
                    customer_name=customer["name"],
                    language=customer["language"],
                    vehicle_model=customer["vehicle_model"],
                    issues=diagnosis["alerts"]
                )
                
                # Auto-book appointment if critical
                audio_b64 = ""
                if diagnosis["status"] == "CRITICAL":
                    appointment = create_appointment({
                        "vehicle_id": vehicle_id,
                        "customer_id": customer["customer_id"],
                        "slot_time": "Tomorrow 10:00 AM",
                        "issue_type": diagnosis["alerts"][0]["issue"],
                        "status": "PENDING_CONFIRMATION",
                        "risk_score": diagnosis["risk_score"]
                    })
                    
                    # Create manufacturing feedback
                    if diagnosis["risk_score"] > 60:
                        create_manufacturing_alert(
                            vehicle_model=customer["vehicle_model"],
                            issue_type=diagnosis["alerts"][0]["issue"],
                            frequency=0.15
                        )
                    
                    # NEW: Generate Voice Audio for Critical Alerts
                    print("🎤 Generating AI Voice Audio...")
                    audio_bytes = text_to_speech(script)
                    if audio_bytes:
                        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
                
                # Send alert back to vehicle
                await websocket.send_json({
                    "type": "ALERT",
                    "diagnosis": diagnosis,
                    "voice_script": script,
                    "appointment_booked": diagnosis["status"] == "CRITICAL"
                })
                
                # Broadcast to all dashboards
                await broadcast_update({
                    "type": "NEW_ALERT",
                    "vehicle_id": vehicle_id,
                    "diagnosis": diagnosis,
                    "timestamp": datetime.utcnow().isoformat(),
                    "audio": audio_b64  # Sending audio data
                })
            
            # Send normal acknowledgment
            else:
                await websocket.send_json({
                    "type": "OK",
                    "status": "NORMAL",
                    "temp": sensor_data.get("engine_temp")
                })
    
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        print(f"❌ Vehicle {vehicle_id} disconnected")

# ==================== WebSocket: Dashboard Updates ====================
@app.websocket("/ws/dashboard")
async def dashboard_stream(websocket: WebSocket):
    """Real-time dashboard updates"""
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)

async def broadcast_update(message: dict):
    """Broadcast to all connected dashboards"""
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except:
            pass

# ==================== REST APIs ====================
@app.get("/")
async def root():
    """Serve dashboard"""
    # UTF-8 Encoding Fix for Windows
    with open("dashboard.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/api/stats")
async def get_stats():
    """Get dashboard statistics"""
    return get_dashboard_stats()

@app.get("/api/alerts")
async def get_alerts():
    """Get recent alerts"""
    return {"alerts": get_recent_alerts(limit=10)}

@app.post("/api/book-service")
async def book_service(request: AppointmentRequest):
    """Manual service booking"""
    appointment = create_appointment({
        "vehicle_id": request.vehicle_id,
        "customer_name": request.customer_name,
        "slot_time": request.slot_time,
        "status": "CONFIRMED"
    })
    return {"success": True, "appointment_id": appointment}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AgentX MVP",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    try:
        # Run the server
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        print("\n🛑 AgentX Server stopped by user.")
    except Exception as e:
        print(f"Error: {e}")