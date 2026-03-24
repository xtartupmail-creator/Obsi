import json
import os
from typing import Dict, Any
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
        acks="all"
    )

def publish(topic: str, key: str, payload: Dict[str, Any]) -> None:
    if BUS_MODE == "redis":
        r.xadd(topic, {"key": key, "payload": json.dumps(payload)}, maxlen=100000, approximate=True)
    else:
        _kafka_producer.send(topic, key=key, value=payload)
        _kafka_producer.flush()
