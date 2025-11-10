import requests
from .config import load_config

DEFAULT_TIMEOUT = (5, 20)

class ApiError(RuntimeError):
    pass

def get_json(url, timeout=DEFAULT_TIMEOUT):
    r = requests.get(url, headers={"accept": "application/json"}, timeout=timeout)
    if r.status_code >= 400:
        raise ApiError(f"GET {url} -> {r.status_code} {r.text[:200]}")
    return r.json()

def post_json(url, timeout=DEFAULT_TIMEOUT):
    r = requests.post(url, headers={"accept": "application/json"}, timeout=timeout)
    if r.status_code >= 400:
        raise ApiError(f"POST {url} -> {r.status_code} {r.text[:200]}")
    return r.json()