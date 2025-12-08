import asyncio
import websockets
import json
import random
import time

VEHICLE_ID = "WB-02-AD-1234"
URI = f"ws://localhost:8000/ws/telematics/{VEHICLE_ID}"

async def simulate_vehicle():
    async with websockets.connect(URI) as websocket:
        print(f"Connected to AgentX Cloud for {VEHICLE_ID}")
        
        while True:
            # Simulate normal driving then sudden overheating
            temp = random.randint(85, 95)
            
            # Simulate a breakdown event randomly
            if random.random() > 0.9: 
                temp = 110 # Critical Overheating
            
            payload = {
                "timestamp": time.time(),
                "engine_temp": temp,
                "rpm": random.randint(2000, 4000),
                "battery_voltage": 12.4,
                "latitude": 22.5726,
                "longitude": 88.3639
            }
            
            await websocket.send(json.dumps(payload))
            print(f"Sent: Temp={temp}°C")
            
            # Listen for server response (Agents)
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                data = json.loads(response)
                if data.get("type") == "ALERT":
                    print("\n--- INCOMING VOICE AGENT ALERT ---")
                    print(f"Agent Script: {data['message']}")
                    print("----------------------------------\n")
            except asyncio.TimeoutError:
                pass
            
            time.sleep(2)

if __name__ == "__main__":
    asyncio.run(simulate_vehicle())