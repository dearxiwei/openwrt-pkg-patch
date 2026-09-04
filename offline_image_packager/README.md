# offline_image_packager

无需 Docker，仅用 `skopeo` 拉取镜像打包为离线包（强制 IPv4 + 代理支持）。

## 特性
- 零 Docker 依赖（仅需 skopeo 二进制）
- 零 Python 第三方依赖（仅标准库）
- 强制 IPv4（socket.getaddrinfo 拦截）
- HTTP 代理支持（--proxy 参数）
- 多 Registry 自动切换：docker.io → quay.io → ghcr.io

## 快速开始

### 安装 skopeo
```bash
./scripts/install_skopeo.sh
```

### 拉取镜像
```bash
# 预览
PYTHONPATH=src python3 scripts/pull_images.py --dry-run --proxy http://127.0.0.1:7890

# 拉取全部
PYTHONPATH=src python3 scripts/pull_images.py --proxy http://127.0.0.1:7890

# 指定输出目录
PYTHONPATH=src python3 scripts/pull_images.py --proxy http://127.0.0.1:7890 -o ./packages
```

## API 文档

### PackConfig
| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `source` | `str` | ✅ | — | 镜像名，如 `alpine`、`library/nginx` |
| `output_dir` | `Path\|str` | ✅ | — | 输出目录 |
| `tag` | `str\|None` | ❌ | `None` | 标签，如 `"latest"` |
| `format` | `str` | ❌ | `"oci-archive"` | `"oci-archive"` 或 `"docker-archive"` |
| `auth_user/pass` | `str\|None` | ❌ | `None` | 私有仓库认证 |
| `ipv4_only` | `bool` | ❌ | `True` | 强制 IPv4 |
| `proxy` | `str\|None` | ❌ | `None` | HTTP代理，如 `"http://127.0.0.1:7890"` |

### OfflineImagePackager
```python
from offline_image_packager import OfflineImagePackager, PackConfig, validate

cfg = PackConfig(source="jlesage/czkawka", output_dir="./packages", tag="latest",
                 format="docker-archive", proxy="http://127.0.0.1:7890")
result = OfflineImagePackager(cfg, proxy=cfg.proxy).pull_and_package()
print(result.dest_path, result.size_bytes)  # Path, int
assert validate(result.dest_path)  # True
```

### 便捷函数
```python
from offline_image_packager import pull, inspect

# 一行拉取
result = pull("jlesage/czkawka", "./packages", tag="latest", proxy="http://127.0.0.1:7890")

# 查看镜像信息
info = inspect("jlesage/czkawka:latest", proxy="http://127.0.0.1:7890")
print(info.name, info.digest[:20], info.size / 1024 / 1024)
```

### validate()
```python
from offline_image_packager import validate
r = validate("packages/czkawka-cn.tar.gz")
print(r.valid, r.manifest_count, r.total_size_bytes)
```

## CLI
```bash
PYTHONPATH=src python3 -m offline_image_packager.cli version
PYTHONPATH=src python3 -m offline_image_packager.cli inspect alpine:latest
PYTHONPATH=src python3 -m offline_image_packager.cli pull alpine:latest -o ./out
```

## 项目结构
```
offline_image_packager/
├── src/offline_image_packager/
│   ├── __init__.py   # 公开 API
│   ├── config.py     # PackConfig
│   ├── registry.py   # Registry 交互（IPv4 + 代理）
│   ├── packager.py   # OfflineImagePackager + pull()/inspect()
│   ├── validator.py  # validate() / quick_check()
│   ├── extractor.py  # extract_to_dir() / list_layers()
│   └── cli.py        # CLI 入口
├── scripts/
│   ├── install_skopeo.sh
│   ├── pull_images.py        # 拉取脚本（多 Registry 自动切换）
│   └── pull_cn_images.sh
├── tests/test_packager.py
├── packages/    # 输出目录（gitignored）
├── tmp/         # 临时目录（gitignored）
├── pyproject.toml
└── README.md
```
