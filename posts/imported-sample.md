---
id: imported-sample
title: Imported Directory Test Story
subtitle: This story verifies importing an external Markdown directory.
author: Jiayi
date: May 15, 2026
minutes: 2
cover: Import test cover
tags: Import, Media, Test
status: published
featured: false
---

## Local image

This image comes from a relative path in the imported directory. After import, it should be copied to `assets/imported/`.

![Local test image](assets/imported/imported-sample/local-image.svg)

## Online image

Online resources are not copied. Their original links are preserved.

![Online placeholder image](https://example.com/online-image.jpg)

## Local video

<video controls src="assets/imported/imported-sample/local-video.mp4"></video>

## Online video

<video controls src="https://example.com/video.mp4"></video>
