from __future__ import annotations

import json
import os
import time

import redis


REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
STREAM = os.getenv("WORKER_STREAM", "finding.ingested.v1")
GROUP = os.getenv("WORKER_GROUP", "correlation-workers")
CONSUMER = os.getenv("WORKER_CONSUMER", "worker-1")


def ensure_group(r: redis.Redis) -> None:
    try:
        r.xgroup_create(STREAM, GROUP, id="0", mkstream=True)
    except redis.ResponseError as exc:
        if "BUSYGROUP" not in str(exc):
            raise


def process_message(data: dict) -> None:
    try:
        payload = json.loads(data.get("payload", "{}"))
    except Exception:
        payload = {}
    # placeholder for enrichment and follow-up dispatch
    print("processed", payload.get("finding_id"), payload.get("decision"), payload.get("score"))


def run() -> None:
    r = redis.from_url(REDIS_URL)
    ensure_group(r)

    while True:
        messages = r.xreadgroup(GROUP, CONSUMER, {STREAM: ">"}, count=20, block=5000)
        if not messages:
            continue
        for _, entries in messages:
            for msg_id, fields in entries:
                process_message(fields)
                r.xack(STREAM, GROUP, msg_id)
        time.sleep(0.1)


if __name__ == "__main__":
    run()
