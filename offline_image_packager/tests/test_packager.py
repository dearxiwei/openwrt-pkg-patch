"""Tests for offline_image_packager."""
import gzip, io, json, tarfile, tempfile
from pathlib import Path
from offline_image_packager.config import PackConfig
from offline_image_packager.packager import OfflineImagePackager
from offline_image_packager.validator import validate

def test_config_defaults():
    cfg = PackConfig(source="alpine", output_dir="/tmp/out")
    assert cfg.source_full == "alpine" and cfg.creds is None and cfg.ipv4_only is True

def test_config_with_tag():
    cfg = PackConfig(source="alpine", output_dir="/tmp/out", tag="3.18")
    assert cfg.source_full == "alpine:3.18"

def test_config_with_creds():
    cfg = PackConfig(source="alpine", output_dir="/tmp/out", auth_user="u", auth_pass="p")
    assert cfg.creds == "u:p"

def test_ensure_dirs():
    with tempfile.TemporaryDirectory() as tmp:
        PackConfig(source="alpine", output_dir=tmp).ensure_dirs()
        assert Path(tmp).exists()

def test_validate_missing():
    assert validate("/nonexistent").valid is False

def test_validate_empty():
    with tempfile.NamedTemporaryFile(suffix=".tar", delete=False) as f:
        with tarfile.open(f.name, "w:gz") as tf: pass
    assert validate(f.name).valid is False; Path(f.name).unlink()

def test_validate_valid():
    with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as f:
        with tarfile.open(f.name, "w:gz") as tf:
            data = json.dumps([{"Config":"abc","RepoTags":["test:latest"]}]).encode()
            info = tarfile.TarInfo(name="manifest.json"); info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
    assert validate(f.name).valid is True; Path(f.name).unlink()

def test_check_skopeo():
    from offline_image_packager.registry import check_skopeo
    assert isinstance(check_skopeo(), bool)

def test_packager_init():
    with tempfile.TemporaryDirectory() as tmp:
        p = OfflineImagePackager(PackConfig(source="alpine:latest", output_dir=tmp))
        assert p.cfg.source_full == "alpine:latest" and p.cfg.ipv4_only is True
