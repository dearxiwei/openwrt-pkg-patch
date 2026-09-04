"""Registry interaction layer - IPv4 only with optional proxy support."""
from __future__ import annotations
import json, os, socket, subprocess
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Optional
from .config import PackConfig

@dataclass
class ImageInfo:
    name: str
    digest: str
    size: int
    media_type: str
    tags: list[str]

_orig_getaddrinfo = socket.getaddrinfo

def _ipv4_getaddrinfo(*args, **kwargs):
    results = _orig_getaddrinfo(*args, **kwargs)
    return [r for r in results if r[0] == socket.AF_INET]

@contextmanager
def _force_ipv4():
    socket.getaddrinfo = _ipv4_getaddrinfo
    try:
        yield
    finally:
        socket.getaddrinfo = _orig_getaddrinfo

def _get_env(proxy: Optional[str] = None) -> dict:
    env = os.environ.copy()
    if proxy:
        env["HTTPS_PROXY"] = proxy
        env["HTTP_PROXY"] = proxy
    return env

def _run_skopeo(args: list[str], timeout: int = 300, proxy: Optional[str] = None) -> subprocess.CompletedProcess[str]:
    cmd = ["skopeo"] + args
    env = _get_env(proxy)
    with _force_ipv4():
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)

def _check_skopeo() -> bool:
    try:
        with _force_ipv4():
            r = subprocess.run(["skopeo", "--version"], capture_output=True, text=True, timeout=10)
        return r.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def inspect(source: str, creds: Optional[str] = None, proxy: Optional[str] = None) -> ImageInfo:
    args = ["inspect", "--format", "json", f"docker://{source}"]
    if creds:
        args.extend(["--creds", creds])
    result = _run_skopeo(args, proxy=proxy)
    if result.returncode != 0:
        raise RuntimeError(f"skopeo inspect failed: {result.stderr.strip()}")
    data = json.loads(result.stdout)
    labels = data.get("Labels") or {}
    return ImageInfo(
        name=data.get("Name", source),
        digest=data.get("Digest", ""),
        size=data.get("Size", 0),
        media_type=data.get("Content-Type", ""),
        tags=list(labels.get("version", [])) if labels.get("version") else [],
    )

def list_tags(source_prefix: str, creds: Optional[str] = None, limit: int = 100, proxy: Optional[str] = None) -> list[str]:
    parts = source_prefix.split("/")
    if len(parts) < 2:
        raise ValueError(f"Invalid source prefix: {source_prefix}")
    registry, repo = parts[0], "/".join(parts[1:])
    import base64, urllib.request
    req = urllib.request.Request(f"https://{registry}/v2/{repo}/tags/list")
    if creds:
        req.add_header("Authorization", f"Basic {base64.b64encode(creds.encode()).decode()}")
    env = _get_env(proxy)
    with _force_ipv4():
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read()).get("tags", [])[:limit]

def check_skopeo() -> bool:
    return _check_skopeo()

def get_skopeo_version() -> str:
    try:
        with _force_ipv4():
            r = subprocess.run(["skopeo", "--version"], capture_output=True, text=True, timeout=10)
        return r.stdout.strip() if r.returncode == 0 else "unknown"
    except Exception:
        return "unknown"
