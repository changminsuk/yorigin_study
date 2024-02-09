import os

from redis.asyncio import ConnectionError, Redis

# https://github.com/python/typeshed/issues/7597#issuecomment-1117572695
redis: "Redis[str]" = Redis.from_url(
    os.environ.get("REDIS_URL", "redis://localhost:6379"),
    decode_responses=True,  # redis.get() 이 byte 대신 str 을 리턴합니다.
    socket_timeout=5,
    retry_on_timeout=True,  # 타임아웃 발생시 재시도 합니다.
    retry_on_error=[ConnectionError],  # 커넥션 에러가 발생했을 때 재시도 합니다.
)
