import redis

from app.config import settings


redis_client = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True
)


def check_rate_limit(
    key: str,
    limit: int
):
    current_count = redis_client.get(key)

    if current_count is None:
        redis_client.setex(key, 60, 1)

        return {
            "allowed": True,
            "remaining": max(limit - 1, 0),
            "reset": 60
        }

    current_count = int(current_count)

    if current_count >= limit:
        return {
            "allowed": False,
            "remaining": 0,
            "reset": 60
        }

    new_count = redis_client.incr(key)

    return {
        "allowed": True,
        "remaining": max(limit - new_count, 0),
        "reset": 60
    }