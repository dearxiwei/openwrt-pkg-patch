"""Offline package validation."""
from __future__ import annotations
import gzip, json, tarfile
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ValidationReport:
    valid: bool
    errors: list[str]
    manifest_count: int
    layer_count: int
    total_size_bytes: int

def validate(package_path) -> ValidationReport:
    path = Path(package_path)
    errors, manifest_count, layer_count, total_size = [], 0, 0, 0
    if not path.exists():
        return ValidationReport(valid=False, errors=[f"File not found: {path}"], manifest_count=0, layer_count=0, total_size_bytes=0)
    try:
        opener = gzip.open if path.suffix == ".gz" else open
        with tarfile.open(fileobj=opener(path, "rb")) as tf:
            members = tf.getmembers()
            names = [m.name for m in members]
            total_size = sum(m.size for m in members)
            if not any("manifest.json" in n for n in names):
                errors.append("Missing manifest.json")
            layer_set = {n for n in names if n.startswith("blobs/sha256/") and not n.endswith(".json")}
            layer_count = len(layer_set)
            manifest_count = sum(1 for n in names if "manifest.json" in n)
    except tarfile.TarError as e:
        errors.append(f"Tar error: {e}")
    except EOFError:
        errors.append("Archive appears truncated")
    except OSError as e:
        errors.append(f"OS error: {e}")
    return ValidationReport(valid=len(errors)==0, errors=errors, manifest_count=manifest_count,
                            layer_count=layer_count, total_size_bytes=total_size)

def quick_check(package_path) -> bool:
    return validate(package_path).valid
