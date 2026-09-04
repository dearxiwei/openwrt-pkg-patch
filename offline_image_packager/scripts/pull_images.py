#!/usr/bin/env python3
"""Pull Chinese font-embedded images (IPv4 only, proxy support)."""
import argparse, gzip, os, shutil, socket, subprocess, sys
from pathlib import Path

# IPv4 only
_orig = socket.getaddrinfo
socket.getaddrinfo = lambda *a, **kw: [r for r in _orig(*a, **kw) if r[0] == socket.AF_INET]

_SCRIPT_DIR = Path(__file__).parent
_PROJECT_DIR = _SCRIPT_DIR.parent
sys.path.insert(0, str(_PROJECT_DIR / "src"))

from offline_image_packager import OfflineImagePackager, PackConfig
from offline_image_packager.registry import check_skopeo

CN_IMAGES = [("jlesage/czkawka:latest", "czkawka-cn.tar.gz"), ("jlesage/krokiet:latest", "krokiet-cn.tar.gz")]
REGISTRIES = ["docker.io", "quay.io", "ghcr.io"]

def find_image(source, proxy=None):
    for reg in REGISTRIES:
        r = subprocess.run(["skopeo","inspect","--format","json",f"docker://{reg}/{source}"],
            capture_output=True, text=True, timeout=10,
            env={**os.environ,"HTTPS_PROXY":proxy or "","HTTP_PROXY":proxy or ""} if proxy else os.environ.copy())
        if r.returncode == 0 and r.stdout: print(f"  Registry: {reg} OK"); return f"{reg}/{source}"
    return None

def tar_to_gz(tar_path, gz_path):
    tmp = Path("/tmp/img_extract_tmp"); tmp.mkdir(exist_ok=True)
    try:
        subprocess.run(["tar","-xf",str(tar_path),"-C",str(tmp)], check=True)
        subprocess.run(["tar","-czf",str(gz_path),"-C",str(tmp),"."], check=True)
    finally: shutil.rmtree(tmp, ignore_errors=True)
    tar_path.unlink(missing_ok=True)

def pull_one(source, output_dir, output_name, registry=None, proxy=None):
    print(f"\n--- [{source}] ---\n  输出: {output_dir}/{output_name}")
    if proxy: print(f"  代理: {proxy}")
    full_source = f"{registry}/{source}" if registry else find_image(source, proxy)
    if not full_source: print("  FAILED: 所有 Registry 均不可达"); return False
    cfg = PackConfig(source=full_source, output_dir=Path(output_dir), format="docker-archive", proxy=proxy)
    result = OfflineImagePackager(cfg, proxy=proxy).pull_and_package()
    if not result.success: print(f"  FAILED: {result.error}"); return False
    tar_to_gz(result.dest_path, Path(output_dir)/output_name)
    print(f"  SUCCESS: {(Path(output_dir)/output_name).stat().st_size/1024/1024:.1f} MB")
    return True

def main():
    p = argparse.ArgumentParser(description="拉取镜像 (IPv4 only)")
    p.add_argument("-o","--output",default="./packages")
    p.add_argument("--source",nargs="*")
    p.add_argument("--registry",choices=REGISTRIES)
    p.add_argument("--proxy",help="HTTP代理, e.g. http://127.0.0.1:7890")
    p.add_argument("--dry-run",action="store_true")
    args = p.parse_args()
    if not check_skopeo(): print("ERROR: skopeo 未安装",file=sys.stderr); sys.exit(1)
    Path(args.output).mkdir(parents=True,exist_ok=True)
    sources = args.source if args.source else [img[0] for img in CN_IMAGES]
    if args.dry_run:
        print("=== Dry Run (IPv4 only) ===")
        for s in sources:
            out = next((img[1] for img in CN_IMAGES if img[0]==s),f"{s}.tar.gz")
            print(f"  {s} -> {args.output}/{out}")
        return
    success, failed = [], []
    for s in sources:
        out = next((img[1] for img in CN_IMAGES if img[0]==s),f"{s}.tar.gz")
        if pull_one(s,args.output,out,args.registry,args.proxy): success.append(out)
        else: failed.append(s)
    print(f"\n=== 完成 === 成功:{len(success)}/{len(sources)}")
    for s in success: print(f"  OK {s}")
    for f in failed: print(f"  FAIL {f}")
    if failed: print("\n提示: --proxy http://127.0.0.1:7890 或使用其他 Registry"); sys.exit(1)

if __name__ == "__main__": main()
