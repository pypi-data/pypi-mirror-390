import random
import string
import base64
import hashlib
import secrets
import requests

def get_random_hash(length: int = 16) -> str:
    pool = string.ascii_letters + string.digits
    return ''.join(random.SystemRandom().choice(pool) for _ in range(length))

def generate_pkce_pair():
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode("utf-8")
    digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("utf-8")
    return code_verifier, code_challenge

def get_discover_openid_configuration_url(url:str, realm:str) -> str:
    return f"{url}/realms/{realm}/.well-known/openid-configuration"

def discover_openid_configuration(url:str, realm:str) -> dict:
    r = requests.get(get_discover_openid_configuration_url(url, realm), timeout=10)
    r.raise_for_status()
    return r.json()