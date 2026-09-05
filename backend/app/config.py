import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./procura.db"
)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-later")