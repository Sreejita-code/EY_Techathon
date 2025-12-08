import asyncio
import websockets
import json
import random

async def run_demo():
    uri = "ws://localhost:8000/ws/vehicle/VH-2024-DEMO"
    
    print(f"⏳ Connecting to {uri} (waiting up to 30s)...")
    
    # INCREASED TIMEOUT: open_timeout=30 gives the server time to wake up
    # PING_INTERVAL: Keeps the connection alive
    async with websockets.connect(uri, open_timeout=30, ping_interval=None) as websocket:
        print("✅ Connected to AgentX. Sending NORMAL data...")
        
        # Phase 1: Normal Driving (5 seconds)
        for _ in range(5):
            data = {
                "engine_temp": random.randint(85, 95),
                "rpm": random.randint(2000, 3000),
                "speed": random.randint(40, 60)
            }
            await websocket.send(json.dumps(data))
            print(f"   [Normal] Temp: {data['engine_temp']}°C")
            await asyncio.sleep(1)

        input("\n⚠️  Press Enter to trigger CRITICAL OVERHEATING >> ")
        
        # Phase 2: Critical Event (Continuous)
        print("🔥 SIMULATING BREAKDOWN...")
        while True:
            data = {
                "engine_temp": random.randint(110, 125), # Dangerous temps!
                "rpm": random.randint(4500, 5000),
                "speed": random.randint(20, 30)
            }
            await websocket.send(json.dumps(data))
            print(f"   [CRITICAL] Temp: {data['engine_temp']}°C - SENT TO AI")
            
            # Listen for AI response (Wait up to 20 seconds for voice generation)
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=20.0)
                msg = json.loads(response)
                if msg.get("type") == "ALERT":
                    print("\n🛑 AI RESPONSE RECEIVED:")
                    print(f"   Diagnosis: {msg['diagnosis']['status']}")
                    print(f"   Script: \"{msg['voice_script']}\"")
                    print(f"   Auto-Booking: {msg['appointment_booked']}")
                    break # Stop after receiving the alert to end demo cleanly
            except asyncio.TimeoutError:
                print("   ... waiting for AI ...")
            except Exception as e:
                print(f"   Error receiving: {e}")
            
            await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        print("\n🛑 Simulation stopped.")
    except Exception as e:
        print(f"\n❌ Connection Failed: {e}")
        print("Tip: Make sure 'uvicorn app:app --reload' is running in the other terminal!")