"""
Audit immutability protection – SQLAlchemy event listener.

Blocks any UPDATE or DELETE operations on AuditLog rows at the ORM level.
"""

from sqlalchemy import event
from sqlalchemy.orm import Session

from models.audit_log import AuditLog


@event.listens_for(Session, "before_flush")
def prevent_audit_modifications(session, flush_context, instances):
    """
    Raise PermissionError if any attempt is made to update or delete an
    AuditLog entry.  This is enforced at the SQLAlchemy session layer so it
    applies to all code paths regardless of which router / service is used.
    """
    for obj in session.dirty:
        if isinstance(obj, AuditLog):
            raise PermissionError("AUDIT LOGS ARE IMMUTABLE – NO UPDATES ALLOWED")

    for obj in session.deleted:
        if isinstance(obj, AuditLog):
            raise PermissionError("AUDIT LOGS CANNOT BE DELETED")
