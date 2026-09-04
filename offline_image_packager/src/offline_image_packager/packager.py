"""Core packaging logic."""
from __future__ import annotations
import shutil, subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from .config import PackConfig
from .registry import check_skopeo, inspect as _inspect_registry
from .registry import ImageInfo

@dataclass
class PackageResult:
    success: bool
    dest_path: Path
    image_info: ImageInfo
    size_bytes: int
    error: Optional[str] = None

class OfflineImagePackager:
    def __init__(self, config: PackConfig, proxy: Optional[str] = None) -> None:
        self.cfg = config
        self.proxy = proxy

    def _build_copy_args(self) -> list[str]:
        args = []
        if self.cfg.auth_user and self.cfg.auth_pass:
            args.extend(["--creds", f"{self.cfg.auth_user}:{self.cfg.auth_pass}"])
        if self.cfg.all_tags:
            args.append("--all")
        return args

    def pull_and_package(self) -> PackageResult:
        self.cfg.ensure_dirs()
        from .registry import _run_skopeo
        copy_args = self._build_copy_args()
        src = f"docker://{self.cfg.source_full}"
        dst = f"{self.cfg.format}:{self.cfg.dest_path}"
        result = _run_skopeo(["copy"] + copy_args + [src, dst], proxy=self.proxy)
        if result.returncode != 0:
            return PackageResult(success=False, dest_path=self.cfg.dest_path,
                image_info=ImageInfo(name=self.cfg.source_full, digest="", size=0, media_type="", tags=[]),
                size_bytes=0, error=result.stderr.strip())
        size = self.cfg.dest_path.stat().st_size if self.cfg.dest_path.exists() else 0
        return PackageResult(success=True, dest_path=self.cfg.dest_path,
            image_info=self.inspect_image(), size_bytes=size)

    def inspect_image(self) -> ImageInfo:
        return _inspect_registry(self.cfg.source_full, self.cfg.creds, proxy=self.proxy)

    def get_image_json(self) -> dict:
        info = self.inspect_image()
        return {"name": info.name, "digest": info.digest, "size": info.size,
                "media_type": info.media_type, "source": self.cfg.source_full,
                "format": self.cfg.format, "dest": str(self.cfg.dest_path)}

    @staticmethod
    def validate(package_path) -> bool:
        from .validator import quick_check
        return quick_check(package_path)

    @staticmethod
    def list_tags(source_prefix: str, creds=None, proxy=None) -> list[str]:
        from .registry import list_tags as _list
        return _list(source_prefix, creds, proxy=proxy)

def pull(source, output_dir=".", tag=None, format="oci-archive",
         auth_user=None, auth_pass=None, all_tags=False, proxy=None) -> PackageResult:
    cfg = PackConfig(source=source, output_dir=Path(output_dir), format=format,
                     tag=tag, auth_user=auth_user, auth_pass=auth_pass, all_tags=all_tags)
    return OfflineImagePackager(cfg, proxy=proxy).pull_and_package()

def inspect(source, tag=None, creds=None, proxy=None) -> ImageInfo:
    full = f"{source}:{tag}" if tag else source
    return _inspect_registry(full, creds, proxy=proxy)
