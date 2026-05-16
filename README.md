# 一间小屋个人博客平台

这是一个极简、Medium 风格的个人博客平台。核心页面仍然是单个 `index.html`，文章可以来自浏览器本地保存，也可以来自 `posts/` 目录里的 Markdown 文件。

## 目录结构

```text
.
├── index.html
├── site.config.json
├── feed.xml
├── posts/
│   ├── index.json
│   ├── static-markdown-demo.md
│   └── imported-sample.md
├── assets/
│   ├── demo-video.mp4
│   ├── midjourney-test.png
│   └── imported/
├── scripts/
│   ├── build_posts_index.py
│   ├── build_rss.py
│   └── import_markdown_dir.py
└── import-report.json
```

## 站点配置

站点名称、作者信息、站点描述和 RSS 地址放在：

```text
site.config.json
```

常用字段：

| 字段 | 作用 |
|---|---|
| `title` | 顶部品牌名、页面标题、RSS 标题 |
| `tagline` | 浏览器首页标题副标题 |
| `description` | 首页摘要、SEO 描述、RSS 描述 |
| `author` | 右侧作者信息 |
| `bio` | 右侧作者简介 |
| `url` | 部署后的站点地址，用于分享链接和 RSS 链接 |
| `rss` | RSS 文件路径，默认 `feed.xml` |

部署到正式域名后，建议把 `url` 改成你的真实地址，例如：

```json
{
  "url": "https://example.com/"
}
```

## 本地预览

在当前目录启动静态服务：

```bash
python3 -m http.server 8766
```

然后打开：

```text
http://localhost:8766/index.html
```

如果浏览器缓存了旧版本，可以加版本参数：

```text
http://localhost:8766/index.html?v=dev
```

## GitHub Pages 部署

部署和维护流程见：

```text
DEPLOYMENT.md
```

仓库已准备 GitHub Actions workflow：推送到 `main` 后，会自动运行 `scripts/build_posts_index.py` 并部署到 GitHub Pages。

## 写一篇静态 Markdown 文章

在 `posts/` 目录新建 `.md` 文件，例如：

```text
posts/my-first-post.md
```

文件顶部写 front matter：

```md
---
id: my-first-post
title: 我的第一篇文章
subtitle: 一句话摘要
author: 林晚舟
date: 2026年5月11日
minutes: 5
cover: 封面占位
tags: 写作, 自托管
status: published
featured: false
---

## 小标题

正文内容。
```

然后重建文章清单：

```bash
python3 scripts/build_posts_index.py
```

刷新页面后，文章会进入首页、搜索、文章页和管理页，同时会更新 RSS 文件。

## Markdown 支持

当前支持：

````md
## 二级标题
### 三级标题

普通段落，支持 [链接](https://example.com) 和 `行内代码`。

> 引用块

- 列表项
- 列表项

![图片说明](assets/example.jpg)

<video controls src="assets/demo-video.mp4"></video>

```js
console.log("code block");
```
````

文章页会根据 Markdown 标题自动生成目录。

## 图片和视频

推荐把资源放在 `assets/`：

```text
assets/my-cover.jpg
assets/my-video.mp4
```

Markdown 中使用相对路径：

```md
![封面](assets/my-cover.jpg)

<video controls src="assets/my-video.mp4"></video>
```

在线资源也支持，导入脚本会保留在线链接：

```md
![在线图片](https://example.com/image.jpg)

<video controls src="https://example.com/video.mp4"></video>
```

注意事项：

| 类型 | 建议 |
|---|---|
| 图片 | `jpg`、`png`、`webp`、`svg` |
| 视频 | 优先 `mp4`，H.264 + AAC 最稳 |
| 大视频 | 建议压缩或截取小样本 |
| 外链资源 | 可能失效或被防盗链 |

## 导入外部 Markdown 目录

如果你已有一批 Markdown 文件，可以用导入脚本：

```bash
python3 scripts/import_markdown_dir.py /path/to/your/markdown-folder
```

脚本会做这些事：

| 行为 | 说明 |
|---|---|
| 复制 Markdown | 导入到 `posts/` |
| 复制本地媒体 | 图片/视频复制到 `assets/imported/<post-id>/` |
| 修正本地路径 | Markdown 中的本地图片/视频路径会改成新路径 |
| 保留在线资源 | `https://...` 不下载，原样保留 |
| 生成报告 | 写入 `import-report.json` |
| 重建清单 | 自动运行 `scripts/build_posts_index.py` |
| 更新 RSS | 自动生成 `feed.xml` |

导入后查看报告：

```text
import-report.json
```

报告会列出：

| 字段 | 含义 |
|---|---|
| `copied` | 已复制的本地媒体 |
| `online` | 保留的在线资源 |
| `missing` | 找不到的本地资源 |

## 管理页说明

管理页里有两种文章：

| 类型 | 来源 | 是否可在线编辑 |
|---|---|---|
| 本地文章 | 浏览器 `localStorage` | 可以 |
| 静态文章 | `posts/*.md` | 不可以，需要改文件 |

静态文章会显示“文件中维护”。如果要编辑，请直接修改对应 `.md` 文件，然后运行：

```bash
python3 scripts/build_posts_index.py
```

## 部署

这是纯静态项目，可以部署到任何静态托管服务。

需要上传：

```text
index.html
site.config.json
feed.xml
posts/
assets/
```

如果也想在服务器上继续生成清单，再上传：

```text
scripts/
```

常见选择：

| 平台 | 说明 |
|---|---|
| GitHub Pages | 适合公开个人站 |
| Netlify | 拖拽目录即可部署 |
| Vercel | 适合 Git 工作流 |
| 任意静态服务器 | 只要能服务 HTML/JSON/MD/媒体文件 |

## 常用命令

```bash
# 本地预览
python3 -m http.server 8766

# 重建 posts/index.json
python3 scripts/build_posts_index.py

# 单独重建 RSS
python3 scripts/build_rss.py

# 导入外部 Markdown 目录
python3 scripts/import_markdown_dir.py /path/to/your/markdown-folder
```
