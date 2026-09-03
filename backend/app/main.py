from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import create_db_and_tables
from app.routers import applications, auth, challenges, documents, pilots, startups

app = FastAPI(title="ProcuraAI")


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

app.include_router(auth.router)
app.include_router(challenges.router)
app.include_router(startups.router)
app.include_router(applications.router)
app.include_router(pilots.router)
app.include_router(documents.router)


@app.get("/")
def home():
    return {"message": "SIH Backend is running"}


@app.get("/health")
def health():
    return {"status": "ok"}
