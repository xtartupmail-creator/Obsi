from __future__ import annotations

import os


class Settings:
    db_url: str = os.getenv("DB_URL", "postgresql+psycopg://app:app@postgres:5432/correlation")
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
    neo4j_user: str = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "password")
    opa_url: str = os.getenv("OPA_URL", "http://opa:8181/v1/data/correlation/ingest")
    service_name: str = os.getenv("SERVICE_NAME", "correlation-api")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
