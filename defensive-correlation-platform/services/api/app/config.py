import os

class Settings:
    db_url = os.getenv("DB_URL", "postgresql+psycopg://app:app@postgres:5432/correlation")
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
    neo4j_user = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
    opa_url = os.getenv("OPA_URL", "http://opa:8181/v1/data/correlation/ingest")

settings = Settings()
