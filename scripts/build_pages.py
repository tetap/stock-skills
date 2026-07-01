#!/usr/bin/env python3
"""构建 GitHub Pages 静态站点到 docs/_site/。"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "docs" / "content"
STATIC = ROOT / "docs" / "site" / "static"
ASSETS = ROOT / "docs" / "assets"
OUT = ROOT / "docs" / "_site"
REPO = "tetap/stock-skills"
SITE_URL = f"https://tetap.github.io/stock-skills"

NAV = [
    ("index", "首页"),
    ("install", "安装"),
    ("usage", "用法"),
    ("cli", "CLI"),
]

PAGES: list[tuple[str, Path]] = [
    ("index", CONTENT / "index.md"),
    ("install", CONTENT / "install.md"),
    ("usage", CONTENT / "usage.md"),
    ("cli", CONTENT / "cli.md"),
]


def _md_html(text: str) -> str:
    try:
        import markdown
    except ImportError as exc:
        raise SystemExit("请先安装: pip install markdown") from exc

    html = markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "nl2br", "sane_lists"],
    )
    # mermaid code blocks -> div.mermaid
    html = re.sub(
        r'<pre><code class="language-mermaid">(.*?)</code></pre>',
        r'<div class="mermaid">\1</div>',
        html,
        flags=re.DOTALL,
    )
    # unescape entities mermaid might need
    html = html.replace("&quot;", '"').replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return html


def _layout(*, page_id: str, title: str, body: str, show_banner: bool) -> str:
    nav_links = []
    for pid, label in NAV:
        cls = ' class="active"' if pid == page_id else ""
        href = "index.html" if pid == "index" else f"{pid}.html"
        nav_links.append(f'<a href="{href}"{cls}>{label}</a>')

    banner = ""
    if show_banner:
        banner = '<img class="hero-banner" src="assets/banner.png" alt="stock-skills banner" />'

    badges = f"""
    <div class="badge-row">
      <a href="https://github.com/{REPO}/actions/workflows/test.yml"><img src="https://github.com/{REPO}/actions/workflows/test.yml/badge.svg" alt="test" /></a>
      <a href="https://github.com/{REPO}/releases"><img src="https://img.shields.io/github/v/release/{REPO}?label=release" alt="release" /></a>
      <a href="https://github.com/{REPO}"><img src="https://img.shields.io/github/stars/{REPO}?style=social" alt="stars" /></a>
    </div>
    """

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="description" content="stock-skills：东方财富 A 股 Agent Skills，/stock 一键全量分析" />
  <title>{title} · stock-skills</title>
  <link rel="stylesheet" href="static/style.css" />
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📈</text></svg>" />
</head>
<body>
  <header class="site-header">
    <div class="header-inner">
      <a class="logo" href="index.html">stock-skills</a>
      <nav>{"".join(nav_links)}</nav>
      <div class="header-links">
        <a href="https://github.com/{REPO}">GitHub</a>
        <a href="https://github.com/{REPO}/blob/master/README.md">README</a>
      </div>
    </div>
  </header>
  <main>
    {banner if show_banner else ""}
    {badges if show_banner else ""}
    <article>{body}</article>
  </main>
  <footer class="site-footer">
    <p><a href="{SITE_URL}">{SITE_URL}</a> · <a href="https://github.com/{REPO}">GitHub</a></p>
    <p>数据仅供参考，不构成投资建议 · MIT License</p>
  </footer>
  <script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
    mermaid.initialize({{ startOnLoad: true, theme: 'dark' }});
  </script>
</body>
</html>
"""


def build() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    (OUT / "static").mkdir()
    (OUT / "assets").mkdir()

    shutil.copy2(STATIC / "style.css", OUT / "static" / "style.css")
    shutil.copy2(ASSETS / "banner.png", OUT / "assets" / "banner.png")
    (OUT / ".nojekyll").touch()

    titles = {
        "index": "首页",
        "install": "安装",
        "usage": "用法",
        "cli": "CLI",
    }

    for page_id, src in PAGES:
        if not src.is_file():
            raise SystemExit(f"缺少页面源文件: {src}")
        md = src.read_text(encoding="utf-8")
        body = _md_html(md)
        html = _layout(
            page_id=page_id,
            title=titles.get(page_id, page_id),
            body=body,
            show_banner=(page_id == "index"),
        )
        out_name = "index.html" if page_id == "index" else f"{page_id}.html"
        (OUT / out_name).write_text(html, encoding="utf-8")
        print(f"[pages] {out_name}")

    print(f"[pages] 输出: {OUT}")


if __name__ == "__main__":
    build()
