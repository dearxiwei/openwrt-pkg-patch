"""CLI entry point."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from .config import PackConfig
from .packager import OfflineImagePackager
from .registry import check_skopeo, get_skopeo_version, inspect as skopeo_inspect

def main(argv=None):
    parser = argparse.ArgumentParser(prog="oip", description="Pull container images without Docker (IPv4 only)")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("pull"); p.add_argument("source"); p.add_argument("-o","--output",default=".")
    p.add_argument("-t","--tag"); p.add_argument("-f","--format",choices=["oci-archive","docker-archive"],default="oci-archive")
    p.add_argument("-u","--user"); p.add_argument("-p","--pass",dest="password"); p.add_argument("--all-tags",action="store_true")
    p = sub.add_parser("inspect"); p.add_argument("source"); p.add_argument("-t","--tag")
    p.add_argument("-u","--user"); p.add_argument("-p","--pass",dest="password")
    p = sub.add_parser("validate"); p.add_argument("package")
    p = sub.add_parser("list-tags"); p.add_argument("source"); p.add_argument("-u","--user"); p.add_argument("-p","--pass",dest="password")
    sub.add_parser("version")
    args = parser.parse_args(argv)
    if args.command == "version":
        print(f"offline_image_packager v0.1.0"); print(f"skopeo: {get_skopeo_version() if check_skopeo() else 'NOT FOUND'}"); print("network: IPv4 only")
        return 0
    if args.command == "pull":
        if not check_skopeo(): print("ERROR: skopeo not found", file=sys.stderr); return 1
        cfg = PackConfig(source=args.source.removeprefix("docker://"), output_dir=Path(args.output), format=args.format, tag=args.tag, auth_user=args.user, auth_pass=args.password, all_tags=args.all_tags)
        result = OfflineImagePackager(cfg).pull_and_package()
        if result.success: print(f"SUCCESS: {result.dest_path}\n  Image: {result.image_info.name}\n  Digest: {result.image_info.digest[:20]}...\n  Size: {result.size_bytes/1024/1024:.1f} MB"); return 0
        else: print(f"FAILED: {result.error}", file=sys.stderr); return 1
    elif args.command == "inspect":
        if not check_skopeo(): print("ERROR: skopeo not found", file=sys.stderr); return 1
        try:
            info = skopeo_inspect(args.source.removeprefix("docker://"), f"{args.user}:{args.password}" if args.user and args.password else None)
            print(json.dumps({"name":info.name,"digest":info.digest,"size_mb":round(info.size/1024/1024,2),"media_type":info.media_type},indent=2)); return 0
        except Exception as e: print(f"ERROR: {e}", file=sys.stderr); return 1
    elif args.command == "validate":
        from .validator import validate
        r = validate(args.package); print(f"Valid: {r.valid}\nManifests: {r.manifest_count}\nLayers: {r.layer_count}\nSize: {r.total_size_bytes/1024/1024:.1f} MB")
        if r.errors:
            for e in r.errors: print(f"  ERROR: {e}"); return 1
        return 0
    elif args.command == "list-tags":
        try:
            tags = OfflineImagePackager.list_tags(args.source.removeprefix("docker://"), f"{args.user}:{args.password}" if args.user and args.password else None)
            for t in tags: print(t); return 0
        except Exception as e: print(f"ERROR: {e}", file=sys.stderr); return 1
    return 0

if __name__ == "__main__": sys.exit(main())
