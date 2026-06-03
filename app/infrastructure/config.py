from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    db_enabled: bool = os.getenv("DB_ENABLED", "true").lower() in {"1", "true", "yes"}
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/eciwise",
    )
    artifacts_dir: Path = Path(os.getenv("ARTIFACTS_DIR", "artifacts"))
    dataset_path: Path = Path(os.getenv("DATASET_PATH", "./ .csv"))
    auto_train: bool = os.getenv("AUTO_TRAIN", "false").lower() in {"1", "true", "yes"}
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # Seguridad: validación del JWT emitido por wise_auth (mismo secreto, HS256).
    jwt_secret: str = os.getenv("JWT_SECRET", "")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    # Orígenes permitidos por CORS (separados por coma). Por defecto, el front local.
    cors_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:4200").split(",")
        if origin.strip()
    )
