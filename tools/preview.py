#!/usr/bin/env python3
"""Render README.md the way GitHub renders it, then open it in a browser.

The markdown goes through GitHub's own Markdown API (via the gh CLI), so
sanitisation, <picture> handling, alerts and heading anchors match the real
profile page. The result is wrapped in a page that mimics the profile layout
and asset URLs are rewritten to local files, so banners that are not pushed
yet still show up.

    python tools/preview.py                       # dark theme, opens browser
    python tools/preview.py --output-dir ../dist  # local stand-in for the output branch
    python tools/preview.py --no-open

Output: .preview/index.html (git-ignored).
"""
from __future__ import annotations

import argparse
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW_MAIN = "https://raw.githubusercontent.com/Niklas-dev/Niklas-dev/main/"
RAW_OUTPUT = "https://raw.githubusercontent.com/Niklas-dev/Niklas-dev/output/"
CSS_DARK = "https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.8.1/github-markdown-dark.min.css"
CSS_LIGHT = "https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.8.1/github-markdown-light.min.css"

PAGE = """<!doctype html>
<html lang="en" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>README preview · Niklas-dev</title>
<link id="mdcss" rel="stylesheet" href="__CSS_DARK__">
<style>
  :root { color-scheme: dark; }
  html[data-theme=light] { color-scheme: light; }
  body { margin: 0; background: #0d1117; color: #e6edf3;
         font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif; }
  html[data-theme=light] body { background: #fff; color: #1f2328; }
  .top { height: 64px; background: #010409; border-bottom: 1px solid #3d444d; display: flex; align-items: center;
         padding: 0 32px; gap: 16px; font-size: 14px; color: #9198a1; }
  html[data-theme=light] .top { background: #f6f8fa; border-color: #d1d9e0; color: #59636e; }
  .top b { color: #e6edf3; font-weight: 600; } html[data-theme=light] .top b { color: #1f2328; }
  .top button { margin-left: auto; background: #212830; color: #e6edf3; border: 1px solid #3d444d; border-radius: 6px;
                padding: 5px 12px; font-size: 13px; cursor: pointer; }
  html[data-theme=light] .top button { background: #f6f8fa; color: #1f2328; border-color: #d1d9e0; }
  .wrap { max-width: 1280px; margin: 0 auto; padding: 24px 32px 80px; display: grid; grid-template-columns: 296px minmax(0, 1fr); gap: 24px; }
  @media (max-width: 1000px) { .wrap { grid-template-columns: 1fr; } .side img { width: 200px !important; height: 200px !important; } }
  .side img { width: 296px; height: 296px; border-radius: 50%; border: 1px solid #3d444d; }
  .name { font-size: 24px; font-weight: 600; margin-top: 16px; line-height: 1.25; }
  .login { font-size: 20px; color: #9198a1; font-weight: 300; }
  .bio { margin: 16px 0; font-size: 16px; }
  .meta { color: #9198a1; font-size: 14px; line-height: 1.8; }
  .box { border: 1px solid #3d444d; border-radius: 6px; overflow: hidden; }
  html[data-theme=light] .box { border-color: #d1d9e0; }
  .boxh { padding: 8px 16px; border-bottom: 1px solid #3d444d; font-size: 12px; color: #9198a1; display: flex; justify-content: space-between; }
  html[data-theme=light] .boxh { border-color: #d1d9e0; color: #59636e; }
  .markdown-body { padding: 32px; background: transparent !important; }
  .markdown-body img { max-width: 100%; }
  .note { font-size: 12px; color: #9198a1; margin-top: 12px; }
</style>
</head>
<body>
<div class="top"><span>github.com / <b>Niklas-dev</b></span><span>·</span><span>README preview, rendered by the GitHub Markdown API</span>
  <button onclick="toggle()">Switch to light</button></div>
<div class="wrap">
  <aside class="side">
    <img src="https://github.com/Niklas-dev.png" alt="avatar">
    <div class="name">Niklas</div>
    <div class="login">Niklas-dev</div>
    <div class="bio">A commit per day keeps the doctor away.</div>
    <div class="meta">41 followers · 8 following<br>Germany</div>
    <div class="note">Sidebar is a mock of GitHub's profile column. Everything on the right is the README.</div>
  </aside>
  <main>
    <div class="box">
      <div class="boxh"><span>Niklas-dev / README.md</span><span>preview</span></div>
      <article class="markdown-body">__BODY__</article>
    </div>
  </main>
</div>
<script>
  const DARK = "__CSS_DARK__", LIGHT = "__CSS_LIGHT__";
  function applyPictures(theme) {
    document.querySelectorAll('picture').forEach(p => {
      const img = p.querySelector('img'); if (!img) return;
      if (!p.dataset.dark) {
        const d = p.querySelector('source[media*="dark"]'), l = p.querySelector('source[media*="light"]');
        p.dataset.dark = d ? d.srcset : img.getAttribute('src');
        p.dataset.light = l ? l.srcset : img.getAttribute('src');
        p.querySelectorAll('source').forEach(s => s.remove());
      }
      img.src = theme === 'light' ? p.dataset.light : p.dataset.dark;
    });
  }
  function toggle() {
    const h = document.documentElement;
    const theme = h.dataset.theme === 'light' ? 'dark' : 'light';
    h.dataset.theme = theme;
    document.getElementById('mdcss').href = theme === 'light' ? LIGHT : DARK;
    document.querySelector('.top button').textContent = theme === 'light' ? 'Switch to dark' : 'Switch to light';
    applyPictures(theme);
  }
  applyPictures('dark');
</script>
</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--output-dir", help="local folder standing in for the `output` branch (its SVGs are copied to .preview/output/)")
    ap.add_argument("--base", help="URL the repo root is reachable at, e.g. http://127.0.0.1:8765/ when serving the folder; "
                                   "defaults to a file:// URL")
    ap.add_argument("--no-open", action="store_true", help="write the file but do not open a browser")
    args = ap.parse_args()

    base = args.base or (ROOT.as_uri() + "/")
    if not base.endswith("/"):
        base += "/"
    out_dir = ROOT / ".preview"
    out_dir.mkdir(exist_ok=True)

    md = (ROOT / "README.md").read_text(encoding="utf-8")
    md = md.replace(RAW_MAIN, base)
    if args.output_dir:
        import shutil
        stand_in = out_dir / "output"
        stand_in.mkdir(exist_ok=True)
        for f in pathlib.Path(args.output_dir).glob("*.svg"):
            shutil.copy(f, stand_in / f.name)
        md = md.replace(RAW_OUTPUT, base + ".preview/output/")

    r = subprocess.run(
        ["gh", "api", "markdown", "-f", "mode=markdown", "-F", "text=@-"],
        input=md, text=True, encoding="utf-8", capture_output=True, shell=(os.name == "nt"),
    )
    if r.returncode != 0:
        sys.stderr.write(r.stderr or "gh api markdown failed\n")
        return r.returncode

    body = r.stdout
    if args.base:
        # GitHub proxies every http(s) image through camo and keeps the original in
        # data-canonical-src. camo cannot reach a local server, so point those back.
        import re

        def uncamo(m: "re.Match[str]") -> str:
            tag = m.group(0)
            orig = re.search(r'data-canonical-src="([^"]+)"', tag)
            if not orig or not orig.group(1).startswith(base):
                return tag
            return re.sub(r'(src|srcset)="https://camo\.githubusercontent\.com/[^"]+"', rf'\1="{orig.group(1)}"', tag)

        body = re.sub(r"<(?:img|source)\b[^>]*>", uncamo, body)

    page = PAGE.replace("__CSS_DARK__", CSS_DARK).replace("__CSS_LIGHT__", CSS_LIGHT).replace("__BODY__", body)
    out = out_dir / "index.html"
    out.write_text(page, encoding="utf-8")
    url = base + ".preview/index.html" if args.base else out.as_uri()
    print(url)
    if not args.no_open:
        if args.base or not hasattr(os, "startfile"):
            import webbrowser
            webbrowser.open(url)
        else:
            os.startfile(out)  # type: ignore[attr-defined]
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
