import json, time, urllib.request, os
from jose import jwt

REGION = os.environ.get("AWS_REGION", "eu-west-2")
USER_POOL_ID = os.environ["USER_POOL_ID"]
APP_CLIENT_ID = os.environ["APP_CLIENT_ID"]

ISSUER = f"https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}"
JWKS_URL = f"{ISSUER}/.well-known/jwks.json"

_JWKS, _JWKS_TS = None, 0

def _load_jwks(force=False):
    global _JWKS, _JWKS_TS
    now = time.time()
    if force or _JWKS is None or now - _JWKS_TS > 3600:
        with urllib.request.urlopen(JWKS_URL, timeout=5) as r:
            _JWKS = json.load(r)["keys"]
            _JWKS_TS = now
    return _JWKS

def _find_key(kid):
    for k in _load_jwks():
        if k.get("kid") == kid:
            return k
    _load_jwks(force=True)
    for k in _JWKS:
        if k.get("kid") == kid:
            return k
    raise ValueError("Signing key not found")

def verify_access_token(auth_header):
    if not auth_header:
        raise ValueError("Missing Authorization header")

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise ValueError("Invalid Authorization header format")

    token = parts[1]

    # --- Extract JWK + find public key ---
    headers = jwt.get_unverified_header(token)
    key = _find_key(headers["kid"])

    # --- Decode + validate core JWT fields ---
    try:
        claims = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=APP_CLIENT_ID,
            issuer=ISSUER
        )
    except Exception as e:
        raise ValueError(f"Token verification failed: {str(e)}")

    # --- Enforce token_use = access ---
    if claims.get("token_use") != "access":
        raise ValueError("Wrong token_use; expected 'access'")

    # --- Enforce expiration explicitly (defense-in-depth) ---
    exp = claims.get("exp")
    if exp and time.time() > exp:
        raise ValueError("Token expired")

    return claims

