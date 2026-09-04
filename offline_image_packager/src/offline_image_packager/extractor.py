"""Extract image contents from offline archives."""
from __future__ import annotations
import gzip, json, tarfile
from pathlib import Path

def extract_to_dir(package_path, dest_dir):
    src, dst = Path(package_path), Path(dest_dir)
    dst.mkdir(parents=True, exist_ok=True)
    opener = gzip.open if src.suffix == ".gz" else open
    with tarfile.open(fileobj=opener(src, "rb")) as tf:
        tf.extractall(path=dst)
    manifest_path = dst / "manifest.json"
    if not manifest_path.exists():
        return {"error": "manifest.json not found"}
    try:
        with open(manifest_path) as f:
            data = json.load(f)
        return {"manifests": data} if isinstance(data, list) else {"manifest": data}
    except (json.JSONDecodeError, OSError) as e:
        return {"error": str(e)}

def list_layers(package_path):
    src, layers = Path(package_path), []
    opener = gzip.open if src.suffix == ".gz" else open
    with tarfile.open(fileobj=opener(src, "rb")) as tf:
        for m in tf.getmembers():
            name = m.name
            if name.startswith("blobs/sha256/") and not name.endswith(".json"):
                digest = name.split("/")[-1]
                if digest.startswith("sha256:") and digest not in layers:
                    layers.append(digest)
    return layers
