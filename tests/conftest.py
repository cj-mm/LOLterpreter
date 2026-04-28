# tests/conftest.py
import sys
import os

# Add the src/ directory to Python's path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
