# chaos-box

Collection of handy utils written in Python 3

## install

推荐使用 uv 安装本项目,

```shell
# install from PyPI
uv tool install chaos-box

# install from Test PyPI
uv tool install chaos-box \
    --index https://test.pypi.org/simple \
    --default-index https://pypi.org/simple
```

## tools

所有命令行工具都可以使用 `-h` 或 `--help` 查看帮助信息, 下面是简要说明:

- `apt-lists`: 统计 `/var/lib/apt/lists` 目录下各仓库的包数量, 可按名称或包数量排序.
- `archive-dirs`: 批量将当前目录下所有文件夹压缩为同名归档文件, 支持多种压缩格式.
- `date-rename`: 将文件重命名为"最后修改日期-原文件名"格式, 支持 dry-run.
- `deb-extract`: 批量解压当前目录下所有 `.deb` 包到同名目录, 支持删除已解压目录.
- `halfwidth`: 将文本文件中的全角标点符号转换为半角标点, 支持原地修改.
- `iconv8`: 批量将文本文件转为 UTF-8 编码, 自动检测原编码, 支持输出目录和覆盖选项.
- `ifstats`: 显示各网卡流量和包计数, 可用正则过滤网卡名称.
- `ipmerge`: 合并并去重输入文件或标准输入中的 IP 地址段, 支持二进制/补零输出.
- `qbt-dump`: 导出 `.torrent` 和 qBittorrent `.fastresume` 文件内容为 JSON 格式.
- `qbt-migrate`: 批量迁移 qBittorrent BT_backup 目录中的 save_path 和 qBt-category, 支持条件过滤和 dry-run.
- `qbt-tracker`: 批量修改 qBittorrent 中 tracker urls, 支持 glob/regex 过滤 torrent.name, regex 替换 tracker urls.
- `qrcode-merge`: 将由 `qrcode-split` 拆分的 QR code 图片合并还原为原文件, 支持并行处理.
- `qrcode-split`: 将任意文本或二进制文件拆分为一系列 QR code 图片, 支持断点续传和并行处理.
- `rotate-images`: 批量生成旋转头像动画 (GIF/MP4), 支持方向, 帧率, 裁剪等参数.
- `shasum-list`: 递归计算指定目录下所有文件的哈希值, 支持多种算法和 .gitignore 忽略.
- `urlencode`: 对输入文本进行 URL 编码或解码, 支持文件或标准输入.
