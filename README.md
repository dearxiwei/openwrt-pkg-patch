# OpenWrt Package Patch

软路由 Docker 镜像补丁索引仓库，支持离线下载和自动 CICD 打补丁。

## 支持的镜像

| 镜像名称 | Docker Hub | 说明 |
|---------|-----------|------|
| czkawka-cn | `jlesage/czkawka` | Czkawka 去重工具 |
| krokiet-cn | `jlesage/krokiet` | Krokiet 图片浏览器 |

## 目录结构

```
openwrt-pkg-patch/
├── .github/workflows/   # CI/CD 工作流
├── scripts/             # 核心脚本模块
│   ├── pull_image.sh    # skopeo 拉取镜像
│   ├── export_image.sh  # 导出 tar 归档
│   ├── import_image.sh  # 导入离线镜像
│   └── generate_checksum.sh  # 生成校验和
├── workflow/            # 编排脚本
│   └── main.sh
├── images/              # 拉取的镜像存储 (gitignored)
└── out/                 # 输出目录
```

## 使用方法

### 本地使用（需要 skopeo）

```bash
# 安装 skopeo
apt-get install -y skopeo

# 拉取所有镜像
./workflow/main.sh all latest

# 拉取单个镜像
./workflow/main.sh czkawka-cn latest

# 导出为 tar
./scripts/export_image.sh czkawka-cn latest

# 离线导入
./scripts/import_image.sh czkawka-cn.tar.gz
```

### GitHub Actions

触发手动构建：
```bash
gh workflow run pull-docker.yml -f image=all
```

## 离线安装流程

1. 在可访问网络的机器上运行 workflow
2. 下载 artifact (`czkawka-image`, `krokiet-image`)
3. 传输到软路由设备
4. 使用 `import_image.sh` 导入
