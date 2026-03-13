import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dashboard.backend.api_routes import router
import os
import sys

# Add parent dir to python path if run standalone
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

app = FastAPI(title="Market Research AI Dashboard API")

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    # Ensure DuckDB directory structure exists if trying to run standalone before db_manager init
    from utils.config import DUCKDB_PATH
    os.makedirs(os.path.dirname(DUCKDB_PATH), exist_ok=True)
    
    uvicorn.run("dashboard.backend.app:app", host="0.0.0.0", port=8000, reload=True)
