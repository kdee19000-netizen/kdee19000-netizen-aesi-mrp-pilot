"""
AESI-MRP Streamlit Dashboard
Provides UI for Fuzie Head interaction and Compliance Dashboard.
"""
import streamlit as st
import requests
from datetime import datetime
import time
import json

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Page config
st.set_page_config(
    page_title="AESI-MRP Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .pending-alert {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .resolved-alert {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .escalated-alert {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def submit_signal(signal_data):
    """Submit a new high-risk signal"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/signals/submit",
            json=signal_data,
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error submitting signal: {str(e)}")
        return None


def log_intervention(signal_id, action, staff_id, notes=""):
    """Log an intervention for a signal"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/signals/intervention",
            json={
                "signal_id": signal_id,
                "action": action,
                "staff_id": staff_id,
                "notes": notes
            },
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error logging intervention: {str(e)}")
        return None


def get_pending_signals():
    """Get all pending signals"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/signals/pending", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching pending signals: {str(e)}")
        return []


def get_all_signals():
    """Get all signals"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/signals", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching signals: {str(e)}")
        return []


def get_audit_trail(signal_id):
    """Get audit trail for a signal"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/audit/{signal_id}", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching audit trail: {str(e)}")
        return []


def get_audit_statistics():
    """Get audit log statistics"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/audit/statistics", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching statistics: {str(e)}")
        return {}


# Main App
st.title("🛡️ AESI-MRP Dashboard")
st.markdown("**Automated Escalation & Safety Intelligence - Mandatory Response Protocol**")

# Check API health
if not check_api_health():
    st.error("⚠️ API is not running. Please start the backend server first: `python -m backend.api`")
    st.stop()

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select Page",
    ["Fuzie Head Interaction", "Compliance Dashboard", "Audit Log", "System Statistics"]
)

# ====================
# FUZIE HEAD INTERACTION
# ====================
if page == "Fuzie Head Interaction":
    st.header("🤖 Fuzie Head - High-Risk Signal Submission")
    st.markdown("Submit new high-risk signals that require immediate attention.")
    
    with st.form("signal_form"):
        st.subheader("Signal Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            student_id = st.text_input("Student ID*", placeholder="e.g., STU-12345")
            risk_type = st.selectbox(
                "Risk Type*",
                ["Behavioral Incident", "Safety Concern", "Mental Health Alert", "Academic Risk", "Other"]
            )
            severity = st.selectbox("Severity*", ["HIGH", "CRITICAL"])
        
        with col2:
            detected_by = st.text_input("Detected By*", placeholder="e.g., AI System, Teacher, Counselor")
            description = st.text_area("Description*", placeholder="Detailed description of the risk...")
        
        submitted = st.form_submit_button("🚨 Submit High-Risk Signal")
        
        if submitted:
            if not all([student_id, risk_type, severity, detected_by, description]):
                st.error("All fields marked with * are required!")
            else:
                signal_data = {
                    "student_id": student_id,
                    "risk_type": risk_type,
                    "severity": severity,
                    "description": description,
                    "detected_by": detected_by,
                    "metadata": {
                        "submitted_via": "Fuzie Head Dashboard",
                        "submission_time": datetime.utcnow().isoformat()
                    }
                }
                
                with st.spinner("Submitting signal..."):
                    result = submit_signal(signal_data)
                    
                if result:
                    st.success(f"✅ Signal submitted successfully!")
                    st.info(f"**Signal ID:** {result['signal_id']}")
                    st.info(f"**Status:** {result['status']}")
                    st.warning("⏱️ 10-minute Responsibility Enforcement timer has started!")
                    st.balloons()

# ====================
# COMPLIANCE DASHBOARD
# ====================
elif page == "Compliance Dashboard":
    st.header("📊 Compliance Dashboard")
    st.markdown("View and manage active PENDING alerts.")
    
    # Auto-refresh
    if st.button("🔄 Refresh Data"):
        st.rerun()
    
    # Get pending signals
    pending_signals = get_pending_signals()
    all_signals = get_all_signals()
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Signals", len(all_signals))
    
    with col2:
        st.metric("⚠️ PENDING", len(pending_signals), help="Requires immediate action")
    
    with col3:
        resolved_count = len([s for s in all_signals if s['status'] == 'RESOLVED'])
        st.metric("✅ RESOLVED", resolved_count)
    
    with col4:
        escalated_count = len([s for s in all_signals if s['status'] == 'ESCALATED'])
        st.metric("🚨 ESCALATED", escalated_count, delta_color="inverse")
    
    st.markdown("---")
    
    # Pending Alerts
    if pending_signals:
        st.subheader("⚠️ Active PENDING Alerts")
        st.warning(f"**{len(pending_signals)} signal(s) require immediate intervention!**")
        
        for signal in pending_signals:
            created_time = datetime.fromisoformat(signal['created_at'].replace('Z', '+00:00'))
            elapsed = (datetime.utcnow() - created_time.replace(tzinfo=None)).total_seconds()
            time_remaining = max(0, 600 - elapsed)  # 10 minutes = 600 seconds
            
            with st.expander(f"🔴 Signal: {signal['signal_id'][:8]}... | Student: {signal['data'].get('student_id', 'N/A')}", expanded=True):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Risk Type:** {signal['data'].get('risk_type', 'N/A')}")
                    st.write(f"**Severity:** {signal['data'].get('severity', 'N/A')}")
                    st.write(f"**Description:** {signal['data'].get('description', 'N/A')}")
                    st.write(f"**Detected By:** {signal['data'].get('detected_by', 'N/A')}")
                    st.write(f"**Created:** {signal['created_at']}")
                    
                    if time_remaining > 0:
                        minutes = int(time_remaining // 60)
                        seconds = int(time_remaining % 60)
                        st.warning(f"⏱️ **Time Remaining:** {minutes}m {seconds}s")
                    else:
                        st.error("⏱️ **Timer Expired** - Signal will be escalated shortly")
                
                with col2:
                    st.subheader("Log Intervention")
                    with st.form(f"intervention_{signal['signal_id']}"):
                        action = st.selectbox(
                            "Action Taken",
                            ["Parent Contacted", "Student Counseling", "Safety Check", "Incident Documented", "Other"],
                            key=f"action_{signal['signal_id']}"
                        )
                        staff_id = st.text_input("Staff ID", key=f"staff_{signal['signal_id']}")
                        notes = st.text_area("Notes", key=f"notes_{signal['signal_id']}")
                        
                        if st.form_submit_button("✅ Log Intervention"):
                            if not staff_id:
                                st.error("Staff ID is required!")
                            else:
                                result = log_intervention(signal['signal_id'], action, staff_id, notes)
                                if result:
                                    st.success("Intervention logged successfully!")
                                    st.rerun()
    else:
        st.success("✅ No pending alerts! All signals have been addressed.")
    
    st.markdown("---")
    
    # Recent Resolved/Escalated
    st.subheader("Recent Activity")
    
    recent_signals = sorted(all_signals, key=lambda x: x['created_at'], reverse=True)[:5]
    
    for signal in recent_signals:
        status = signal['status']
        if status == 'RESOLVED':
            st.markdown(f"""
            <div class="resolved-alert">
                <strong>✅ RESOLVED:</strong> {signal['signal_id'][:8]}... | 
                Student: {signal['data'].get('student_id', 'N/A')} | 
                Intervention: {signal.get('intervention', 'N/A')}
            </div>
            """, unsafe_allow_html=True)
        elif status == 'ESCALATED':
            st.markdown(f"""
            <div class="escalated-alert">
                <strong>🚨 ESCALATED TO TIER 2:</strong> {signal['signal_id'][:8]}... | 
                Student: {signal['data'].get('student_id', 'N/A')} | 
                Reason: Timer expired without intervention
            </div>
            """, unsafe_allow_html=True)

# ====================
# AUDIT LOG
# ====================
elif page == "Audit Log":
    st.header("📜 Immutable Audit Log")
    st.markdown("View cryptographically-secured audit trail for all system events.")
    
    # Signal selector
    all_signals = get_all_signals()
    
    if all_signals:
        signal_options = ["All Signals"] + [s['signal_id'] for s in all_signals]
        selected_signal = st.selectbox("Select Signal", signal_options)
        
        if selected_signal == "All Signals":
            st.subheader("Recent Audit Entries (Last 50)")
            try:
                response = requests.get(f"{API_BASE_URL}/api/audit?limit=50", timeout=5)
                audit_entries = response.json()
            except:
                audit_entries = []
        else:
            st.subheader(f"Audit Trail for Signal: {selected_signal}")
            audit_entries = get_audit_trail(selected_signal)
        
        if audit_entries:
            for entry in audit_entries:
                with st.expander(f"{entry['event_type']} - {entry['timestamp']}"):
                    st.write(f"**Entry ID:** {entry['id']}")
                    st.write(f"**Signal ID:** {entry['signal_id']}")
                    st.write(f"**Event Type:** {entry['event_type']}")
                    st.write(f"**Timestamp:** {entry['timestamp']}")
                    st.write(f"**Hash:** `{entry['hash']}`")
                    st.write(f"**Previous Hash:** `{entry.get('previous_hash', 'None (first entry)')}`")
                    st.write("**Data:**")
                    st.json(entry['data'])
        else:
            st.info("No audit entries found.")
    else:
        st.info("No signals in the system yet.")

# ====================
# SYSTEM STATISTICS
# ====================
elif page == "System Statistics":
    st.header("📈 System Statistics")
    st.markdown("Overview of system health and audit log integrity.")
    
    stats = get_audit_statistics()
    
    if stats:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Audit Log Statistics")
            st.metric("Total Audit Entries", stats.get('total_entries', 0))
            st.metric("Unique Signals", stats.get('unique_signals', 0))
            
            chain_valid = stats.get('chain_valid', False)
            if chain_valid:
                st.success("✅ Audit Chain Integrity: VALID")
            else:
                st.error("❌ Audit Chain Integrity: COMPROMISED")
        
        with col2:
            st.subheader("Events by Type")
            events_by_type = stats.get('events_by_type', {})
            
            if events_by_type:
                for event_type, count in events_by_type.items():
                    st.metric(event_type, count)
            else:
                st.info("No events recorded yet.")
        
        # System health
        st.markdown("---")
        st.subheader("System Health")
        
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            health = response.json()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("API Status", health.get('status', 'unknown').upper())
            
            with col2:
                st.metric("Total Signals", health.get('total_signals', 0))
            
            with col3:
                if health.get('audit_log_integrity', False):
                    st.success("Audit Log: ✅ Valid")
                else:
                    st.error("Audit Log: ❌ Invalid")
        except:
            st.error("Unable to fetch system health.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
    <p>AESI-MRP System v1.0.0 | Deterministic & Auditable for Insurance Underwriters</p>
    <p>⚠️ All actions are logged with cryptographic timestamps for compliance verification</p>
</div>
""", unsafe_allow_html=True)
