"""
Integration tests for AESI-MRP API
"""
import unittest
import tempfile
import os
from fastapi.testclient import TestClient

from backend.api import app, audit_log, mrp_engine


class TestAPI(unittest.TestCase):
    """Test cases for the FastAPI endpoints"""
    
    def setUp(self):
        """Set up test client"""
        self.client = TestClient(app)
        
        # Reduce timeout for faster tests
        mrp_engine.ESCALATION_TIMEOUT = 2
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["service"], "AESI-MRP API")
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("audit_log_integrity", data)
    
    def test_submit_signal(self):
        """Test submitting a new signal"""
        signal_data = {
            "student_id": "STU-123",
            "risk_type": "Behavioral Incident",
            "severity": "HIGH",
            "description": "Test incident",
            "detected_by": "Test System"
        }
        
        response = self.client.post("/api/signals/submit", json=signal_data)
        self.assertEqual(response.status_code, 201)
        
        data = response.json()
        self.assertIn("signal_id", data)
        self.assertEqual(data["status"], "PENDING")
    
    def test_log_intervention(self):
        """Test logging an intervention"""
        # First, submit a signal
        signal_data = {
            "student_id": "STU-456",
            "risk_type": "Safety Concern",
            "severity": "CRITICAL",
            "description": "Test",
            "detected_by": "Test"
        }
        
        submit_response = self.client.post("/api/signals/submit", json=signal_data)
        signal_id = submit_response.json()["signal_id"]
        
        # Log intervention
        intervention_data = {
            "signal_id": signal_id,
            "action": "Parent Contacted",
            "staff_id": "STAFF-789",
            "notes": "Test intervention"
        }
        
        response = self.client.post("/api/signals/intervention", json=intervention_data)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["status"], "RESOLVED")
    
    def test_log_intervention_invalid_signal(self):
        """Test logging intervention for non-existent signal"""
        intervention_data = {
            "signal_id": "invalid-id",
            "action": "Test",
            "staff_id": "STAFF-123"
        }
        
        response = self.client.post("/api/signals/intervention", json=intervention_data)
        self.assertEqual(response.status_code, 404)
    
    def test_get_pending_signals(self):
        """Test getting pending signals"""
        # Submit multiple signals
        for i in range(3):
            signal_data = {
                "student_id": f"STU-{i}",
                "risk_type": "Test",
                "severity": "HIGH",
                "description": "Test",
                "detected_by": "Test"
            }
            self.client.post("/api/signals/submit", json=signal_data)
        
        response = self.client.get("/api/signals/pending")
        self.assertEqual(response.status_code, 200)
        
        signals = response.json()
        self.assertGreaterEqual(len(signals), 3)
    
    def test_get_signal_by_id(self):
        """Test getting a specific signal"""
        # Submit a signal
        signal_data = {
            "student_id": "STU-789",
            "risk_type": "Test",
            "severity": "HIGH",
            "description": "Test",
            "detected_by": "Test"
        }
        
        submit_response = self.client.post("/api/signals/submit", json=signal_data)
        signal_id = submit_response.json()["signal_id"]
        
        # Get the signal
        response = self.client.get(f"/api/signals/{signal_id}")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["signal_id"], signal_id)
        self.assertEqual(data["data"]["student_id"], "STU-789")
    
    def test_get_signal_not_found(self):
        """Test getting non-existent signal"""
        response = self.client.get("/api/signals/invalid-id")
        self.assertEqual(response.status_code, 404)
    
    def test_get_all_signals(self):
        """Test getting all signals"""
        response = self.client.get("/api/signals")
        self.assertEqual(response.status_code, 200)
        
        signals = response.json()
        self.assertIsInstance(signals, list)
    
    def test_get_audit_trail(self):
        """Test getting audit trail for a signal"""
        # Submit a signal
        signal_data = {
            "student_id": "STU-AUDIT",
            "risk_type": "Test",
            "severity": "HIGH",
            "description": "Test",
            "detected_by": "Test"
        }
        
        submit_response = self.client.post("/api/signals/submit", json=signal_data)
        signal_id = submit_response.json()["signal_id"]
        
        # Get audit trail
        response = self.client.get(f"/api/audit/{signal_id}")
        self.assertEqual(response.status_code, 200)
        
        entries = response.json()
        self.assertGreater(len(entries), 0)
        self.assertEqual(entries[0]["signal_id"], signal_id)
    
    def test_get_audit_statistics(self):
        """Test getting audit statistics"""
        response = self.client.get("/api/audit/statistics")
        self.assertEqual(response.status_code, 200)
        
        stats = response.json()
        self.assertIn("total_entries", stats)
        self.assertIn("chain_valid", stats)


if __name__ == "__main__":
    unittest.main()
