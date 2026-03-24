from __future__ import annotations

import time
from dataclasses import dataclass

import redis


@dataclass(slots=True)
class TokenBucket:
    redis_client: redis.Redis
    limit: int = 60
    window_seconds: int = 60

    def allow(self, key: str) -> bool:
        now_ms = int(time.time() * 1000)
        bucket = f"ratelimit:{key}"
        pipe = self.redis_client.pipeline()
        pipe.zremrangebyscore(bucket, 0, now_ms - (self.window_seconds * 1000))
        pipe.zadd(bucket, {str(now_ms): now_ms})
        pipe.zcard(bucket)
        pipe.expire(bucket, self.window_seconds)
        _, _, count, _ = pipe.execute()
        return int(count) <= self.limit
