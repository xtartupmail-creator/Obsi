import time
import redis
import os

r = redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379/0"))


def run():
    while True:
        msg = r.blpop(["finding.ingested.v1"], timeout=5)
        if msg:
            print("received:", msg[1][:200])
        time.sleep(0.2)


if __name__ == "__main__":
    run()
