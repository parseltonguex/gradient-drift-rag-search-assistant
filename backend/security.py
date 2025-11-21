import time
from fastapi import Request
from fastapi.responses import JSONResponse

# Simple in-memory per-IP rate limiter.
# Good enough for development and overnight safety.

# { ip_address: [timestamps] }
REQUEST_COUNTS = {}

# Allowed requests per time window
MAX_REQUESTS = 20          # adjust as needed
WINDOW_SECONDS = 60        # 1 minute

def _client_ip(request: Request) -> str:
    """Extract client IP from headers (API Gateway uses X-Forwarded-For)."""
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host or "unknown"

async def enforce_rate_limit(request: Request):
    """
    Throttle repeated requests from the same IP.
    Returns JSONResponse(429) if over limit, else None.
    """
    ip = _client_ip(request)
    now = time.time()

    # Keep only timestamps within the active window
    REQUEST_COUNTS.setdefault(ip, [])
    REQUEST_COUNTS[ip] = [t for t in REQUEST_COUNTS[ip] if now - t < WINDOW_SECONDS]

    if len(REQUEST_COUNTS[ip]) >= MAX_REQUESTS:
        return JSONResponse(
            {"error": "Rate limit exceeded. Try again later."},
            status_code=429
        )

    REQUEST_COUNTS[ip].append(now)
    return None
