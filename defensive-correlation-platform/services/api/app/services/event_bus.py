from __future__ import annotations

import json
import os
from typing import Any, Dict

import redis

BUS_MODE = os.getenv("BUS_MODE", "redis")
r = redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379/0"))

_kafka_producer = None
if BUS_MODE == "kafka":
    from kafka import KafkaProducer

    _kafka_producer = KafkaProducer(
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP", "kafka:9092"),
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda v: v.encode("utf-8"),
        acks="all",
    )


def publish(topic: str, key: str, payload: Dict[str, Any]) -> None:
    if BUS_MODE == "redis":
        r.xadd(topic, {"key": key, "payload": json.dumps(payload)}, maxlen=100000, approximate=True)
    else:
        assert _kafka_producer is not None
        _kafka_producer.send(topic, key=key, value=payload)
        _kafka_producer.flush()


def publish_ingested(tenant_id: str, finding_id: str, asset_id: str, score: float, decision: str, reasons: list[str]) -> None:
    publish(
        topic="finding.ingested.v1",
        key=finding_id,
        payload={
            "schema_version": "v1",
            "tenant_id": tenant_id,
            "finding_id": finding_id,
            "asset_id": asset_id,
            "score": score,
            "decision": decision,
            "reasons": reasons,
        },
    )
