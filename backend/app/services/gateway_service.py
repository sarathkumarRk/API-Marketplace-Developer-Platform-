import time
import httpx


def forward_request(
    base_url: str,
    path: str,
    method: str,
    headers: dict | None = None,
    params: dict | None = None,
    body: dict | None = None
):
    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"

    start_time = time.time()

    response = httpx.request(
        method=method,
        url=url,
        headers=headers,
        params=params,
        json=body
    )

    response_time_ms = int(
        (time.time() - start_time) * 1000
    )

    return {
        "status_code": response.status_code,
        "headers": dict(response.headers),
        "body": response.text,
        "response_time_ms": response_time_ms
    }