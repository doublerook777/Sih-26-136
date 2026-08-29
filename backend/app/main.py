from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import create_db_and_tables
app = FastAPI()
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "SIH Backend is running"}

@app.get("/health")
def health():
    return {"status": "ok"}