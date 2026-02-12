"""
Immutable Audit Log with Cryptographic Timestamps
Provides tamper-evident logging for all AESI-MRP system events.
"""
import hashlib
import json
import threading
from datetime import datetime
from typing import Dict, List, Optional
import sqlite3
import os


class AuditLog:
    """
    Immutable audit log with cryptographic hash chain.
    Each log entry is hashed with the previous entry's hash to create a tamper-evident chain.
    """
    
    def __init__(self, db_path: str = "audit_log.db"):
        """
        Initialize the audit log.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database for audit logs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                data TEXT NOT NULL,
                hash TEXT NOT NULL,
                previous_hash TEXT,
                UNIQUE(id)
            )
        """)
        
        # Create index for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_signal_id ON audit_entries(signal_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_entries(timestamp)
        """)
        
        conn.commit()
        conn.close()
    
    def _get_last_hash(self) -> Optional[str]:
        """Get the hash of the last audit entry for chain validation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT hash FROM audit_entries 
            ORDER BY id DESC LIMIT 1
        """)
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def _compute_hash(self, signal_id: str, event_type: str, timestamp: str, 
                     data: str, previous_hash: Optional[str]) -> str:
        """
        Compute cryptographic hash for an audit entry.
        
        Args:
            signal_id: Signal identifier
            event_type: Type of event
            timestamp: ISO format timestamp
            data: JSON-encoded event data
            previous_hash: Hash of previous entry (for chain)
            
        Returns:
            SHA-256 hash hex string
        """
        # Create deterministic string for hashing
        hash_input = f"{signal_id}|{event_type}|{timestamp}|{data}|{previous_hash or ''}"
        
        # Compute SHA-256 hash
        return hashlib.sha256(hash_input.encode()).hexdigest()
    
    def log_event(self, signal_id: str, event_type: str, data: Dict) -> int:
        """
        Log an event to the immutable audit log.
        
        Args:
            signal_id: Signal identifier
            event_type: Type of event (e.g., SIGNAL_RECEIVED, INTERVENTION_LOGGED)
            data: Dictionary containing event details
            
        Returns:
            Entry ID in the audit log
        """
        with self._lock:
            # Get current timestamp
            timestamp = datetime.utcnow().isoformat()
            
            # Serialize data to JSON
            data_json = json.dumps(data, sort_keys=True)
            
            # Get previous hash for chain validation
            previous_hash = self._get_last_hash()
            
            # Compute hash for this entry
            entry_hash = self._compute_hash(
                signal_id, event_type, timestamp, data_json, previous_hash
            )
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO audit_entries 
                (signal_id, event_type, timestamp, data, hash, previous_hash)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (signal_id, event_type, timestamp, data_json, entry_hash, previous_hash))
            
            entry_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return entry_id
    
    def get_entries_for_signal(self, signal_id: str) -> List[Dict]:
        """
        Get all audit entries for a specific signal.
        
        Args:
            signal_id: Signal identifier
            
        Returns:
            List of audit entry dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, signal_id, event_type, timestamp, data, hash, previous_hash
            FROM audit_entries
            WHERE signal_id = ?
            ORDER BY id ASC
        """, (signal_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        entries = []
        for row in rows:
            entries.append({
                "id": row[0],
                "signal_id": row[1],
                "event_type": row[2],
                "timestamp": row[3],
                "data": json.loads(row[4]),
                "hash": row[5],
                "previous_hash": row[6]
            })
        
        return entries
    
    def get_all_entries(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get all audit entries (optionally limited).
        
        Args:
            limit: Maximum number of entries to return (most recent first)
            
        Returns:
            List of audit entry dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if limit:
            cursor.execute("""
                SELECT id, signal_id, event_type, timestamp, data, hash, previous_hash
                FROM audit_entries
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
        else:
            cursor.execute("""
                SELECT id, signal_id, event_type, timestamp, data, hash, previous_hash
                FROM audit_entries
                ORDER BY id DESC
            """)
        
        rows = cursor.fetchall()
        conn.close()
        
        entries = []
        for row in rows:
            entries.append({
                "id": row[0],
                "signal_id": row[1],
                "event_type": row[2],
                "timestamp": row[3],
                "data": json.loads(row[4]),
                "hash": row[5],
                "previous_hash": row[6]
            })
        
        return entries
    
    def verify_chain_integrity(self) -> bool:
        """
        Verify the integrity of the audit log chain.
        
        Returns:
            True if chain is valid, False if tampered with
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, signal_id, event_type, timestamp, data, hash, previous_hash
            FROM audit_entries
            ORDER BY id ASC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        previous_hash = None
        for row in rows:
            entry_id, signal_id, event_type, timestamp, data, stored_hash, stored_previous_hash = row
            
            # Verify previous hash matches
            if stored_previous_hash != previous_hash:
                return False
            
            # Recompute hash and verify
            computed_hash = self._compute_hash(
                signal_id, event_type, timestamp, data, previous_hash
            )
            
            if computed_hash != stored_hash:
                return False
            
            previous_hash = stored_hash
        
        return True
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about the audit log.
        
        Returns:
            Dictionary with statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM audit_entries")
        total_entries = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT signal_id) FROM audit_entries")
        unique_signals = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT event_type, COUNT(*) 
            FROM audit_entries 
            GROUP BY event_type
        """)
        events_by_type = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            "total_entries": total_entries,
            "unique_signals": unique_signals,
            "events_by_type": events_by_type,
            "chain_valid": self.verify_chain_integrity()
        }
