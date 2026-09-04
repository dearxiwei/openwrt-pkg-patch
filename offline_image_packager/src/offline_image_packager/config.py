"""Configuration management for offline image packaging."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class PackConfig:
    source: str
    output_dir: Path
    format: str = "oci-archive"
    tag: Optional[str] = None
    auth_user: Optional[str] = None
    auth_pass: Optional[str] = None
    all_tags: bool = False
    compress: bool = True
    skip_validation: bool = False
    ipv4_only: bool = True
    proxy: Optional[str] = None

    def __post_init__(self) -> None:
        self.output_dir = Path(self.output_dir).expanduser().resolve()

    @property
    def source_full(self) -> str:
        if self.tag:
            return f"{self.source}:{self.tag}"
        return self.source

    @property
    def creds(self) -> Optional[str]:
        if self.auth_user and self.auth_pass:
            return f"{self.auth_user}:{self.auth_pass}"
        return None

    @property
    def dest_path(self) -> Path:
        name = Path(self.source_full).name.replace("/", "_").replace(":", "_")
        return self.output_dir / f"{name}.tar"

    def ensure_dirs(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
