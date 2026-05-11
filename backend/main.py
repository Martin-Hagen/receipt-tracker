import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(title="Receipt Expense Tracker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path(__file__).parent / "data"
UPLOADS_DIR = Path(__file__).parent / "uploads"


@app.on_event("startup")
async def startup_event():
    DATA_DIR.mkdir(exist_ok=True)
    UPLOADS_DIR.mkdir(exist_ok=True)
    expenses_file = DATA_DIR / "expenses.json"
    if not expenses_file.exists():
        expenses_file.write_text("[]", encoding="utf-8")


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "message": "Receipt Expense Tracker API is running"}


# TODO Phase 2-3: 라우터 등록
# from backend.routers import upload, expenses, summary
# app.include_router(upload.router, prefix="/api")
# app.include_router(expenses.router, prefix="/api")
# app.include_router(summary.router, prefix="/api")
