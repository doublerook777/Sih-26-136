import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./procura.db"
)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)