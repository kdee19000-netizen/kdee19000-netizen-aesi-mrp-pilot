"""
AESI-MRP Core Engine
Handles High-Risk signal intake, record locking, timer-based escalation, and intervention logging.
"""
import threading
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from enum import Enum

from .audit_log import AuditLog


class SignalStatus(Enum):
    """Signal status enumeration"""
    PENDING = "PENDING"
    RESOLVED = "RESOLVED"
    ESCALATED = "ESCALATED"


class SignalRecord:
    """Represents a high-risk signal record"""
    
    def __init__(self, signal_id: str, data: Dict):
        self.signal_id = signal_id
        self.data = data
        self.status = SignalStatus.PENDING
        self.created_at = datetime.utcnow()
        self.timer_started_at = datetime.utcnow()
        self.resolved_at: Optional[datetime] = None
        self.intervention: Optional[str] = None
        self.escalated = False
        self.timer_thread: Optional[threading.Thread] = None


class MRPEngine:
    """
    Core MRP Engine for AESI-MRP system.
    Handles signal intake, record locking, timer-based escalation, and interventions.
    """
    
    # 10-minute timer (in seconds)
    ESCALATION_TIMEOUT = 600  # 10 minutes
    
    def __init__(self, audit_log: AuditLog):
        self.signals: Dict[str, SignalRecord] = {}
        self.audit_log = audit_log
        self._lock = threading.Lock()
    
    def receive_signal(self, signal_data: Dict) -> str:
        """
        Receive a high-risk signal and lock it to PENDING status.
        Starts the 10-minute responsibility enforcement timer.
        
        Args:
            signal_data: Dictionary containing signal information
            
        Returns:
            signal_id: Unique identifier for the signal
        """
        signal_id = str(uuid.uuid4())
        
        with self._lock:
            # Create and lock the record
            record = SignalRecord(signal_id, signal_data)
            self.signals[signal_id] = record
            
            # Log the initial detection
            self.audit_log.log_event(
                signal_id=signal_id,
                event_type="SIGNAL_RECEIVED",
                data={
                    "signal_data": signal_data,
                    "status": SignalStatus.PENDING.value,
                    "timestamp": record.created_at.isoformat()
                }
            )
            
            # Start escalation timer
            self._start_escalation_timer(signal_id)
            
        return signal_id
    
    def _start_escalation_timer(self, signal_id: str):
        """Start the 10-minute escalation timer for a signal"""
        
        def timer_callback():
            """Callback function that runs after timeout"""
            time.sleep(self.ESCALATION_TIMEOUT)
            
            with self._lock:
                if signal_id in self.signals:
                    record = self.signals[signal_id]
                    
                    # Only escalate if still PENDING
                    if record.status == SignalStatus.PENDING:
                        self._escalate_signal(signal_id)
        
        # Start timer thread
        timer_thread = threading.Thread(target=timer_callback, daemon=True)
        timer_thread.start()
        
        self.signals[signal_id].timer_thread = timer_thread
    
    def _escalate_signal(self, signal_id: str):
        """
        Escalate a signal to Tier 2 supervisor.
        Called automatically when timer expires without intervention.
        """
        if signal_id not in self.signals:
            return
        
        record = self.signals[signal_id]
        record.status = SignalStatus.ESCALATED
        record.escalated = True
        
        # Log escalation event
        self.audit_log.log_event(
            signal_id=signal_id,
            event_type="ESCALATED_TO_TIER2",
            data={
                "reason": "No intervention logged within 10 minutes",
                "escalated_at": datetime.utcnow().isoformat(),
                "timer_started_at": record.timer_started_at.isoformat()
            }
        )
    
    def log_intervention(self, signal_id: str, intervention_data: Dict) -> bool:
        """
        Log a verified intervention and unlock the record.
        
        Args:
            signal_id: The signal ID
            intervention_data: Dictionary containing intervention details
                             (e.g., {"action": "Parent Contacted", "staff_id": "123"})
        
        Returns:
            True if intervention logged successfully, False otherwise
        """
        with self._lock:
            if signal_id not in self.signals:
                return False
            
            record = self.signals[signal_id]
            
            # Can't log intervention on already escalated signal
            if record.status == SignalStatus.ESCALATED:
                return False
            
            # Update record
            record.status = SignalStatus.RESOLVED
            record.resolved_at = datetime.utcnow()
            record.intervention = intervention_data.get("action", "Unknown")
            
            # Log intervention
            self.audit_log.log_event(
                signal_id=signal_id,
                event_type="INTERVENTION_LOGGED",
                data={
                    "intervention": intervention_data,
                    "resolved_at": record.resolved_at.isoformat(),
                    "elapsed_time_seconds": (record.resolved_at - record.created_at).total_seconds()
                }
            )
            
            return True
    
    def get_signal(self, signal_id: str) -> Optional[SignalRecord]:
        """Get a signal record by ID"""
        with self._lock:
            return self.signals.get(signal_id)
    
    def get_pending_signals(self) -> List[SignalRecord]:
        """Get all signals with PENDING status"""
        with self._lock:
            return [
                record for record in self.signals.values()
                if record.status == SignalStatus.PENDING
            ]
    
    def get_all_signals(self) -> List[SignalRecord]:
        """Get all signal records"""
        with self._lock:
            return list(self.signals.values())
    
    def get_signal_status(self, signal_id: str) -> Optional[str]:
        """Get the status of a signal"""
        with self._lock:
            if signal_id in self.signals:
                return self.signals[signal_id].status.value
            return None
