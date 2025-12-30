import uvicorn
import os
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Now import
from app.main_csv import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    
    print("=" * 60)
    print("🚀 BSK Training Optimization API (CSV-Based)")
    print("=" * 60)
    print(f"📍 Host: 0.0.0.0")
    print(f"🔌 Port: {port}")
    print(f"📊 Data: CSV files")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )