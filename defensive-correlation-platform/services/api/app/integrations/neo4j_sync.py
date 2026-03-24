from __future__ import annotations

from pathlib import Path
from typing import Any

from neo4j import GraphDatabase

from app.config import settings


class Neo4jSync:
    def __init__(self) -> None:
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
        self.query = Path(__file__).resolve().parents[3] / "neo4j" / "sync.cypher"

    def sync(self, payload: dict[str, Any]) -> None:
        query = self.query.read_text(encoding="utf-8")
        with self.driver.session() as session:
            session.run(query, payload)

    def close(self) -> None:
        self.driver.close()
