"""
Hash Chain Utilities

Helpers for building and verifying Merkle-style hash chains.
"""

import hashlib
from typing import List, Tuple


def compute_event_hash(payload: str) -> str:
    """Return a SHA-512 hex digest of *payload*."""
    return hashlib.sha512(payload.encode()).hexdigest()


def build_chain(events: List[str]) -> List[Tuple[str, str]]:
    """
    Build an ordered hash chain from a list of event payloads.

    Returns a list of (prev_hash, event_hash) tuples.
    """
    chain: List[Tuple[str, str]] = []
    prev = "genesis"
    for event in events:
        h = compute_event_hash(f"{event}|{prev}")
        chain.append((prev, h))
        prev = h
    return chain


def verify_chain(chain: List[Tuple[str, str]], events: List[str]) -> bool:
    """
    Verify that *chain* matches the given *events* list.

    Returns True if the chain is intact, False otherwise.
    """
    if len(chain) != len(events):
        return False

    prev = "genesis"
    for (stored_prev, stored_hash), event in zip(chain, events):
        if stored_prev != prev:
            return False
        expected_hash = compute_event_hash(f"{event}|{prev}")
        if stored_hash != expected_hash:
            return False
        prev = stored_hash

    return True
