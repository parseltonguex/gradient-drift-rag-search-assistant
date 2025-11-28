# backend/auth_verify.py

from jose import jwk, jwt
from jose.utils import base64url_decode
import requests
import logging
import json
from typing import Dict

logger = logging.getLogger()

REGION = "eu-west-2"
USER_POOL_ID = "eu-west-2_yJBTFgb5Q"
APP_CLIENT_ID = "5hh9g0pqhog16bkangcp4p26o2"

JWKS_URL = f"https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json"

# Cache JWKs for reuse
_jwks = None

def verify_access_token(auth_header: str) -> Dict:
    if not auth_header or not auth_header.startswith("Bearer "):
        raise Exception("Missing or invalid Authorization header")

    token = auth_header.split(" ")[1]

    global _jwks
    if _jwks is None:
        response = requests.get(JWKS_URL)
        if response.status_code != 200:
            raise Exception("Failed to fetch JWKS from Cognito")
        _jwks = response.json()["keys"]

    headers = jwt.get_unverified_headers(token)
    kid = headers["kid"]

    # Find the correct public key
    key = next((k for k in _jwks if k["kid"] == kid), None)
    if not key:
        raise Exception("Public key not found in JWKS")

    public_key = jwk.construct(key)

    message, encoded_signature = token.rsplit(".", 1)
    decoded_signature = base64url_decode(encoded_signature.encode("utf-8"))

    if not public_key.verify(message.encode("utf-8"), decoded_signature):
        raise Exception("Signature verification failed")

    claims = jwt.get_unverified_claims(token)

    # Validate standard claims
    if claims["exp"] < int(__import__("time").time()):
        raise Exception("Token has expired")

    if claims["aud"] != APP_CLIENT_ID:
        raise Exception("Token was not issued for this audience")

    logger.info(f"Token verified: {claims}")
    return claims
