import uvicorn
import os

# Import CSV-based main instead of database main
from app.main_csv import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    
    print(f"🚀 Starting BSK API (CSV-Based) on 0.0.0.0:{port}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )