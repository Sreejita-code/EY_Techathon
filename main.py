# File: main.py
from fastapi import FastAPI, WebSocket
from db_connect import log_telematics, create_appointment  # <--- UPDATED IMPORT
from agents import analyze_telematics, generate_call_script
from pydantic import BaseModel
import json

app = FastAPI(title="AgentX Backend")

class AppointmentRequest(BaseModel):
    customer_id: str
    slot_time: str
    issue_type: str

# --- WebSocket for Real-time Telematics ---
@app.websocket("/ws/telematics/{vehicle_id}")
async def telematics_endpoint(websocket: WebSocket, vehicle_id: str):
    await websocket.accept()
    print(f"Vehicle {vehicle_id} connected.")
    
    try:
        while True:
            # 1. Receive Data Stream
            data = await websocket.receive_text()
            sensor_data = json.loads(data)
            sensor_data["vehicle_id"] = vehicle_id
            
            # 2. Layer 3: Store Data
            log_telematics(sensor_data)
            
            # 3. Layer 2: Diagnosis Agent Analysis
            diagnosis = analyze_telematics(sensor_data)
            
            if diagnosis["status"] == "RISK":
                print(f"⚠ ANOMALY DETECTED for {vehicle_id}: {diagnosis['issues']}")
                
                # Generate Script
                script = generate_call_script("Bhaskar", diagnosis['issues'][0], "Hero Splendor")
                
                # Send alert back to simulator
                await websocket.send_json({
                    "type": "ALERT",
                    "message": script,
                    "issues": diagnosis["issues"]
                })

    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        await websocket.close()

@app.post("/api/book-service")
async def book_service(request: AppointmentRequest):
    result = create_appointment(request.dict())
    return {"status": "confirmed", "booking_id": str(result.inserted_id)}

@app.get("/")
def read_root():
    return {"status": "AgentX Core Online"}