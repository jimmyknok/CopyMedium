---
id: static-markdown-demo
title: Publishing a Story from a Markdown File
subtitle: This story comes from posts/static-markdown-demo.md and demonstrates file-based static publishing.
author: Jiayi
date: May 14, 2026
minutes: 3
cover: Static Markdown example
tags: Markdown, Static publishing, Self-hosted
status: published
featured: true
---

## Why file-based publishing

When stories grow, keeping content in separate Markdown files becomes more reliable. You can write in any editor and keep the whole `posts/` directory under Git.

> Static publishing is not about complexity. It is about moving content from browser cache back into a file system you can keep.

## Image assets

Images can live in the `assets/` directory and be referenced with relative paths in Markdown.

![Test image copied from the Midjourney folder](assets/midjourney-test.png)

## Basic workflow

- Put stories in `posts/`
- Put images and videos in `assets/`
- Register story metadata in `posts/index.json`
- Refresh the page and the story appears on Home, Search, and the article page

## Video assets

Videos can also live in `assets/`. This demo uses a short sample so the page loads faster.

<video controls src="assets/demo-video.mp4"></video>

To insert your own video, use HTML:

```html
<video controls src="assets/demo-video.mp4"></video>
```
