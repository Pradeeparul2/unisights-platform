from fastapi import Request
from typing import Optional


def get_client_ip(request: Request) -> Optional[str]:
    """
    Resolve client IP address from request headers.

    Priority:
    - Cloudflare
    - X-Forwarded-For
    - Direct client
    """

    return (
        request.headers.get("cf-connecting-ip")
        or request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        or request.client.host if request.client else None
    )
