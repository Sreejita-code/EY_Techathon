from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
# Alternatively use: from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

# Initialize LLM (Gemini or OpenAI as per architecture [cite: 97])
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

# --- Diagnosis Agent (Rule + AI Hybrid) ---
def analyze_telematics(data: dict):
    """
    Analyzes sensor data for anomalies.
    Rule-based first for speed, can escalate to LLM for complex patterns.
    """
    alerts = []
    
    # Simple Rule-Based Logic (e.g., Coolant Temp > 105C)
    if data.get("engine_temp", 0) > 105:
        alerts.append("CRITICAL: Engine Overheating Detected")
    
    if data.get("battery_voltage", 12) < 11.5:
        alerts.append("WARNING: Low Battery Voltage")
        
    if alerts:
        return {"status": "RISK", "issues": alerts}
    return {"status": "NORMAL", "issues": []}

# --- Customer Engagement Agent (Script Generator) ---
booking_prompt = PromptTemplate(
    input_variables=["customer_name", "issue", "vehicle_model"],
    template="""
    You are an empathetic service assistant for AgentX.
    The customer {customer_name}'s {vehicle_model} has a critical issue: {issue}.
    
    Generate a short, polite script to call the customer. 
    1. Inform them of the specific issue detected by telematics.
    2. Explain the risk (e.g., breakdown).
    3. Propose a service slot for tomorrow at 10 AM.
    4. Keep it conversational and under 50 words.
    """
)

chain = booking_prompt | llm

def generate_call_script(customer_name, issue, vehicle_model):
    """Generates the text for ElevenLabs TTS."""
    return chain.invoke({
        "customer_name": customer_name,
        "issue": issue,
        "vehicle_model": vehicle_model
    }).content