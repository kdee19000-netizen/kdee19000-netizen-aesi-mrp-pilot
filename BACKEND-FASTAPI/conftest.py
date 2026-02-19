"""
pytest configuration – add BACKEND-FASTAPI to sys.path so tests can import modules.
"""

import sys
import os

# Ensure the BACKEND-FASTAPI directory is on the path
sys.path.insert(0, os.path.dirname(__file__))
