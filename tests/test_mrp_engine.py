"""
Unit tests for AESI-MRP Core Engine
"""
import unittest
import time
import tempfile
import os
from datetime import datetime

from backend.mrp_engine import MRPEngine, SignalStatus
from backend.audit_log import AuditLog


class TestAuditLog(unittest.TestCase):
    """Test cases for the Audit Log"""
    
    def setUp(self):
        """Create a temporary database for testing"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.audit_log = AuditLog(self.temp_db.name)
    
    def tearDown(self):
        """Clean up temporary database"""
        os.unlink(self.temp_db.name)
    
    def test_log_event(self):
        """Test logging an event"""
        entry_id = self.audit_log.log_event(
            signal_id="test-123",
            event_type="TEST_EVENT",
            data={"key": "value"}
        )
        
        self.assertIsNotNone(entry_id)
        self.assertGreater(entry_id, 0)
    
    def test_get_entries_for_signal(self):
        """Test retrieving entries for a specific signal"""
        signal_id = "test-456"
        
        # Log multiple events
        self.audit_log.log_event(signal_id, "EVENT1", {"data": 1})
        self.audit_log.log_event(signal_id, "EVENT2", {"data": 2})
        self.audit_log.log_event("other-signal", "EVENT3", {"data": 3})
        
        entries = self.audit_log.get_entries_for_signal(signal_id)
        
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]["event_type"], "EVENT1")
        self.assertEqual(entries[1]["event_type"], "EVENT2")
    
    def test_hash_chain_integrity(self):
        """Test that hash chain is properly maintained"""
        # Log several events
        self.audit_log.log_event("sig1", "EVENT1", {"data": 1})
        self.audit_log.log_event("sig2", "EVENT2", {"data": 2})
        self.audit_log.log_event("sig3", "EVENT3", {"data": 3})
        
        # Verify chain integrity
        is_valid = self.audit_log.verify_chain_integrity()
        self.assertTrue(is_valid)
    
    def test_statistics(self):
        """Test audit log statistics"""
        self.audit_log.log_event("sig1", "EVENT1", {"data": 1})
        self.audit_log.log_event("sig1", "EVENT2", {"data": 2})
        self.audit_log.log_event("sig2", "EVENT3", {"data": 3})
        
        stats = self.audit_log.get_statistics()
        
        self.assertEqual(stats["total_entries"], 3)
        self.assertEqual(stats["unique_signals"], 2)
        self.assertTrue(stats["chain_valid"])


class TestMRPEngine(unittest.TestCase):
    """Test cases for the MRP Engine"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.audit_log = AuditLog(self.temp_db.name)
        self.engine = MRPEngine(self.audit_log)
        
        # Reduce timeout for faster tests
        self.engine.ESCALATION_TIMEOUT = 2  # 2 seconds for testing
    
    def tearDown(self):
        """Clean up"""
        os.unlink(self.temp_db.name)
    
    def test_receive_signal(self):
        """Test receiving a new high-risk signal"""
        signal_data = {
            "student_id": "STU-123",
            "risk_type": "Behavioral Incident",
            "severity": "HIGH"
        }
        
        signal_id = self.engine.receive_signal(signal_data)
        
        self.assertIsNotNone(signal_id)
        
        # Verify signal was created
        signal = self.engine.get_signal(signal_id)
        self.assertIsNotNone(signal)
        self.assertEqual(signal.status, SignalStatus.PENDING)
        self.assertEqual(signal.data, signal_data)
    
    def test_log_intervention_success(self):
        """Test successfully logging an intervention"""
        signal_data = {"student_id": "STU-456"}
        signal_id = self.engine.receive_signal(signal_data)
        
        intervention_data = {
            "action": "Parent Contacted",
            "staff_id": "STAFF-789"
        }
        
        success = self.engine.log_intervention(signal_id, intervention_data)
        
        self.assertTrue(success)
        
        signal = self.engine.get_signal(signal_id)
        self.assertEqual(signal.status, SignalStatus.RESOLVED)
        self.assertEqual(signal.intervention, "Parent Contacted")
        self.assertIsNotNone(signal.resolved_at)
    
    def test_log_intervention_invalid_signal(self):
        """Test logging intervention for non-existent signal"""
        success = self.engine.log_intervention(
            "invalid-id",
            {"action": "Test"}
        )
        
        self.assertFalse(success)
    
    def test_automatic_escalation(self):
        """Test automatic escalation after timer expires"""
        signal_data = {"student_id": "STU-ESCALATE"}
        signal_id = self.engine.receive_signal(signal_data)
        
        # Wait for escalation timeout
        time.sleep(3)  # Wait longer than the 2-second timeout
        
        signal = self.engine.get_signal(signal_id)
        self.assertEqual(signal.status, SignalStatus.ESCALATED)
        self.assertTrue(signal.escalated)
    
    def test_no_escalation_after_intervention(self):
        """Test that intervention prevents escalation"""
        signal_data = {"student_id": "STU-NO-ESC"}
        signal_id = self.engine.receive_signal(signal_data)
        
        # Log intervention before timeout
        self.engine.log_intervention(signal_id, {"action": "Handled"})
        
        # Wait to see if escalation occurs
        time.sleep(3)
        
        signal = self.engine.get_signal(signal_id)
        self.assertEqual(signal.status, SignalStatus.RESOLVED)
        self.assertFalse(signal.escalated)
    
    def test_cannot_intervene_after_escalation(self):
        """Test that intervention cannot be logged after escalation"""
        signal_data = {"student_id": "STU-LATE"}
        signal_id = self.engine.receive_signal(signal_data)
        
        # Wait for escalation
        time.sleep(3)
        
        # Try to log intervention after escalation
        success = self.engine.log_intervention(signal_id, {"action": "Too Late"})
        
        self.assertFalse(success)
    
    def test_get_pending_signals(self):
        """Test retrieving pending signals"""
        # Create multiple signals
        sig1 = self.engine.receive_signal({"student_id": "STU-1"})
        sig2 = self.engine.receive_signal({"student_id": "STU-2"})
        sig3 = self.engine.receive_signal({"student_id": "STU-3"})
        
        # Resolve one
        self.engine.log_intervention(sig2, {"action": "Resolved"})
        
        pending = self.engine.get_pending_signals()
        pending_ids = [s.signal_id for s in pending]
        
        self.assertEqual(len(pending), 2)
        self.assertIn(sig1, pending_ids)
        self.assertNotIn(sig2, pending_ids)
        self.assertIn(sig3, pending_ids)
    
    def test_audit_log_integration(self):
        """Test that all events are logged to audit log"""
        signal_data = {"student_id": "STU-AUDIT"}
        signal_id = self.engine.receive_signal(signal_data)
        
        # Get audit entries
        entries = self.audit_log.get_entries_for_signal(signal_id)
        
        # Should have SIGNAL_RECEIVED event
        self.assertGreater(len(entries), 0)
        self.assertEqual(entries[0]["event_type"], "SIGNAL_RECEIVED")
        
        # Log intervention
        self.engine.log_intervention(signal_id, {"action": "Test"})
        
        entries = self.audit_log.get_entries_for_signal(signal_id)
        
        # Should now have INTERVENTION_LOGGED event too
        event_types = [e["event_type"] for e in entries]
        self.assertIn("SIGNAL_RECEIVED", event_types)
        self.assertIn("INTERVENTION_LOGGED", event_types)


if __name__ == "__main__":
    unittest.main()
