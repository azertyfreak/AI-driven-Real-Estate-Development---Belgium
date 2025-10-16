"""
Belgian Housing AI - Auto Start
"""

import subprocess
import sys
import os
from pathlib import Path

print("=" * 70)
print("🚀 BELGIAN HOUSING AI")
print("=" * 70)

# Install dependencies
print("\n📦 Installing dependencies...")
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", "backend/requirements.txt"])
print("✅ Dependencies installed")

# Initialize database if needed
db_path = Path("backend/belgian_housing_full.db")
if not db_path.exists():
    print("\n📊 Initializing database...")
    os.chdir("backend")
    subprocess.run([sys.executable, "statbel_integration.py"])
    os.chdir("..")
    print("✅ Database ready")
else:
    print("\n✅ Database found")

# Start API
print("\n🌐 Starting API server...")
print("=" * 70 + "\n")
os.chdir("backend")
subprocess.run([sys.executable, "flask_api.py"])
