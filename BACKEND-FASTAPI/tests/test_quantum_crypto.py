"""
Tests for the QuantumCryptoService.
"""

import pytest

from services.quantum_crypto import QuantumCryptoService


@pytest.fixture
def crypto():
    return QuantumCryptoService()


def test_generate_hash_is_deterministic(crypto):
    """Same input must always produce the same SHA-512 hash."""
    h1 = crypto.generate_hash("hello world")
    h2 = crypto.generate_hash("hello world")
    assert h1 == h2


def test_generate_hash_differs_for_different_inputs(crypto):
    assert crypto.generate_hash("aaa") != crypto.generate_hash("bbb")


def test_hybrid_sign_produces_signature(crypto):
    sig = crypto.hybrid_sign("test payload")
    assert sig
    assert "rsa:" in sig


def test_verify_valid_signature(crypto):
    payload = "quantum test payload"
    sig = crypto.hybrid_sign(payload)
    assert crypto.verify_signature(payload, sig) is True


def test_verify_tampered_payload_fails(crypto):
    payload = "original payload"
    sig = crypto.hybrid_sign(payload)
    assert crypto.verify_signature("tampered payload", sig) is False


def test_verify_invalid_signature_string(crypto):
    assert crypto.verify_signature("some payload", "not-a-real-signature") is False
