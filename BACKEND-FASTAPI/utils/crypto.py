"""
Cryptographic utilities

Thin wrappers used by other modules; delegates to the quantum crypto service.
"""

import logging

from services.quantum_crypto import QuantumCryptoService, crypto_service

logger = logging.getLogger(__name__)

_initialized = False


def init_crypto():
    """Called once at startup to confirm the crypto service is ready."""
    global _initialized
    if _initialized:
        return
    from services.quantum_crypto import PQ_AVAILABLE

    logger.info(
        "Crypto service ready. post_quantum=%s",
        PQ_AVAILABLE,
    )
    _initialized = True


def generate_hash(data: str) -> str:
    return crypto_service.generate_hash(data)


def hybrid_sign(payload: str) -> str:
    return crypto_service.hybrid_sign(payload)


def verify_signature(payload: str, signature: str) -> bool:
    return crypto_service.verify_signature(payload, signature)
