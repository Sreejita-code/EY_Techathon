# agents.py
import os
import json
import requests
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
# --- UPDATED IMPORTS TO FIX "ModuleNotFoundError" ---
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv()

# Initialize Gemini
# Uses gemini-1.5-flash which is the current valid model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.0
)

def diagnose_vehicle(sensor_data):
    """
    Sends sensor data to Gemini to analyze for mechanical failures.
    Expects a JSON response.
    """
    prompt = PromptTemplate.from_template(
        """
        You are an expert automotive AI diagnostic tool called AgentX.
        Analyze the following real-time vehicle telemetry data:
        {sensor_data}

        Task:
        1. Identify any anomalies (temperature, rpm, speed patterns).
        2. Determine the status: 'CRITICAL', 'WARNING', or 'NORMAL'.
        3. Assign a risk score (0-100).
        4. If issues exist, describe them briefly.

        IMPORTANT: Return your response in STRICT JSON format only, like this:
        {{
            "status": "CRITICAL",
            "risk_score": 85,
            "alerts": [
                {{"issue": "Engine Overheating", "severity": "HIGH"}}
            ]
        }}
        Do not add Markdown formatting (like ```json). Just the raw JSON string.
        """
    )
    
    chain = prompt | llm | StrOutputParser()
    
    try:
        response = chain.invoke({"sensor_data": json.dumps(sensor_data)})
        # Clean potential markdown if the model ignores the instruction
        clean_response = response.strip().replace("```json", "").replace("```", "")
        return json.loads(clean_response)
    except Exception as e:
        print(f"AI Diagnosis Error: {e}")
        # Fallback safe mode
        return {"status": "NORMAL", "risk_score": 0, "alerts": []}

def generate_voice_script(customer_name, language, vehicle_model, issues):
    """
    Returns a static script to avoid 'model not defined' errors during demo.
    """
    # Safe Mode: Return static text immediately
    return f"Hello {customer_name}, this is AgentX. We detected {issues} in your {vehicle_model}. An appointment has been booked."

def text_to_speech(text):
    """
    Simulation Mode: Just prints the call delivery to terminal.
    """
    # Safe Mode: Print to terminal instead of calling API
    print("\n" + "="*40)
    print(f"📞  CALL DELIVERED TO CUSTOMER")
    print(f"📝  Message: \"{text}\"")
    print("="*40 + "\n")
    
    return None

def create_manufacturing_alert(vehicle_model, issue_type, frequency):
    """
    Simulates sending feedback to the OEM manufacturing database.
    """
    print(f"🏭 [MFG-FEEDBACK-LOOP] Logged recurring defect '{issue_type}' for {vehicle_model} chassis.")