# database.py (FAST DEMO VERSION)
from datetime import datetime
import uuid

# In-memory storage for the demo
telematics_log = []
diagnosis_log = []
appointments = []

def log_telematics(data):
    """Store raw sensor data in memory"""
    telematics_log.append(data)

def create_appointment(data):
    """Mock appointment creation"""
    appt_id = str(uuid.uuid4())[:8]
    data['appointment_id'] = appt_id
    data['status'] = data.get('status', 'PENDING')
    data["created_at"] = datetime.utcnow()
    # Insert at the beginning so it shows up first
    appointments.insert(0, data)
    return appt_id

def log_diagnosis(data):
    """Store diagnosis results"""
    diagnosis_log.insert(0, data) # Newest first

def get_recent_alerts(limit=10):
    """Retrieve recent critical diagnoses"""
    # Return the 'diagnosis' part plus timestamp/vehicle_id wrapper
    return diagnosis_log[:limit]

def get_dashboard_stats():
    """Calculate stats for the dashboard"""
    # Count critical alerts (mock logic)
    critical_count = len([d for d in diagnosis_log if d['diagnosis']['status'] == 'CRITICAL'])
    
    return {
        "total_vehicles": 1, 
        "alerts_today": len(diagnosis_log),
        "critical_alerts": critical_count,
        "appointments_booked": len(appointments),
        "manufacturing_issues": int(critical_count * 0.2), 
        "recent_alerts": diagnosis_log[:5],
        "recent_appointments": appointments[:5]
    }

def get_customer_by_vehicle(vehicle_id):
    """Mock customer database"""
    return {
        "customer_id": "CUST_001",
        "name": "Rajesh Kumar", # Changed to generic name for demo
        "language": "Hindi",
        "vehicle_model": "Hero XPulse 200"
    }