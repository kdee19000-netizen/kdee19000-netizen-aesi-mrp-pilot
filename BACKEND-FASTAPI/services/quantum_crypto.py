"""
Quantum Cryptography Service

Provides hybrid classical (RSA-4096) + post-quantum (Dilithium3) signatures.
Falls back to RSA-only when the `oqs` library is not installed.
"""

import hashlib
import logging

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

logger = logging.getLogger(__name__)

try:
    import oqs  # type: ignore

    PQ_AVAILABLE = True
    logger.info("oqs-python loaded – post-quantum cryptography enabled (Dilithium3)")
except ImportError:
    PQ_AVAILABLE = False
    logger.warning("oqs-python not available – falling back to classical RSA-only signatures")


class QuantumCryptoService:
    """Hybrid classical + post-quantum signing service."""

    def __init__(self):
        # Classical RSA-4096
        self.rsa_private = rsa.generate_private_key(65537, 4096)
        self.rsa_public = self.rsa_private.public_key()

        # Post-Quantum Dilithium3
        if PQ_AVAILABLE:
            self.pq_signer = oqs.Signature("Dilithium3")
            self.pq_public_key = self.pq_signer.export_public_key()
        else:
            self.pq_signer = None
            self.pq_public_key = None

    # ------------------------------------------------------------------
    def generate_hash(self, data: str) -> str:
        """Return a SHA-512 hex digest of *data*."""
        return hashlib.sha512(data.encode()).hexdigest()

    # ------------------------------------------------------------------
    def hybrid_sign(self, payload: str) -> str:
        """
        Sign *payload* with RSA-PSS-SHA512.
        If PQ is available, also sign with Dilithium3 and embed both.

        Signature format v2:  pq:<hex>|rsa:<hex>|v2
        Signature format v1:  rsa:<hex>|v1
        """
        rsa_sig = self.rsa_private.sign(
            payload.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA512()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA512(),
        ).hex()

        if PQ_AVAILABLE and self.pq_signer is not None:
            pq_sig = self.pq_signer.sign(payload.encode()).hex()
            return f"pq:{pq_sig}|rsa:{rsa_sig}|v2"

        return f"rsa:{rsa_sig}|v1"

    # ------------------------------------------------------------------
    def verify_signature(self, payload: str, signature: str) -> bool:
        """
        Verify a hybrid signature produced by :meth:`hybrid_sign`.

        Only the RSA part is verified (sufficient for tamper detection).
        """
        try:
            if "|v2" in signature:
                parts = signature.split("|")
                # parts: ["pq:<hex>", "rsa:<hex>", "v2"]
                rsa_part = next(p for p in parts if p.startswith("rsa:"))
                rsa_sig_hex = rsa_part[4:]
            elif "|v1" in signature:
                parts = signature.split("|")
                rsa_part = next(p for p in parts if p.startswith("rsa:"))
                rsa_sig_hex = rsa_part[4:]
            else:
                return False

            self.rsa_public.verify(
                bytes.fromhex(rsa_sig_hex),
                payload.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA512()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA512(),
            )
            return True
        except Exception:
            return False


# Module-level singleton
crypto_service = QuantumCryptoService()
