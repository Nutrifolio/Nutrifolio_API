from fastapi.requests import Request


def get_cache(request: Request) -> "Redis":
    return request.app.state._cache_conn_pool
