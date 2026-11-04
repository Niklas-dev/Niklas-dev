#!/usr/bin/env python3
"""Generate the SVG banners used by the profile README.

Standard library only. Run from anywhere:

    python tools/build_assets.py              # writes assets/
    python tools/build_assets.py --options    # also writes .preview/options/ (design variants)

Design: a monochrome terminal. Near-black, off-white text, one green accent
(ZeroSubnet's #00ff87), 1px rules, monospace everywhere. No gradients, no
glows. Each image has at most one slow, purposeful motion; all motion is
disabled for viewers who prefer reduced motion. Everything is hand-drawn
SVG, so it keeps working for as long as GitHub serves this repository.
Fonts fall back through system stacks because GitHub's image proxy does
not load web fonts.
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"

MONO = ("'Cascadia Code','JetBrains Mono','Fira Code','SF Mono',Menlo,Consolas,"
        "'DejaVu Sans Mono','Liberation Mono',monospace")

# palette (module globals so variants can swap them)
BG = "#090b0d"       # near-black panel background
SURF = "#0f1215"     # raised surface
LINE = "#1c2126"     # 1px rules and borders
TEXT = "#e6e8eb"     # primary text
SOFT = "#c2c7cd"     # secondary text
DIM = "#8a9099"      # labels
MUTE = "#4f565e"     # faint labels
GREEN = "#00ff87"    # the one accent (ZeroSubnet green)
CELL = "#22272d"     # inactive cell

HERO_STYLE = "grid"  # grid | wave | type

BASE_CSS = """
text { font-family: %s; }
@media (prefers-reduced-motion: reduce) {
  * { animation: none !important; }
  .type { clip-path: none !important; }
  .fade, .in, .boot { opacity: 1 !important; }
}
""" % MONO


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg(w: int, h: int, body: str, css: str = "", label: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">\n'
        f"<style><![CDATA[{BASE_CSS}{css}]]></style>\n{body}\n</svg>\n"
    )


def panel(w: int, h: int, r: int = 8) -> str:
    return f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="{r}" fill="{BG}" stroke="{LINE}"/>'


def text(x: float, y: float, s: str, size: float, fill: str = TEXT, weight: int = 400,
         anchor: str = "start", cls: str = "", extra: str = "") -> str:
    c = f' class="{cls}"' if cls else ""
    w = f' font-weight="{weight}"' if weight != 400 else ""
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return f'<text{c} x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}"{w}{a}{extra}>{esc(s)}</text>'


def spans(x: float, y: float, parts: list[tuple[str, str]], size: float, cls: str = "", extra: str = "") -> str:
    c = f' class="{cls}"' if cls else ""
    inner = "".join(f'<tspan fill="{col}">{esc(s)}</tspan>' for s, col in parts)
    return f'<text{c} x="{x:.1f}" y="{y:.1f}" font-size="{size}" xml:space="preserve"{extra}>{inner}</text>'


def cursor_span() -> str:
    return f'<tspan class="cur" fill="{GREEN}">█</tspan>'


def dl(t: float) -> str:
    return f' style="animation-delay:{t:.2f}s"'


# --------------------------------------------------------------------------- hero
def hero(style: str | None = None) -> str:
    style = style or HERO_STYLE
    W, H = 900, 280
    css = """
.in { opacity: 0; animation: fin .8s cubic-bezier(.2,.6,.2,1) forwards; }
.i1 { animation-delay: .05s; } .i2 { animation-delay: .2s; } .i3 { animation-delay: .38s; }
.i4 { animation-delay: .56s; } .i5 { animation-delay: .74s; } .i6 { animation-delay: .92s; }
@keyframes fin { to { opacity: 1; } }
.boot { opacity: 0; animation: boot .5s ease-out forwards, cell 6.4s ease-in-out 2.2s infinite; }
@keyframes boot { to { opacity: .16; } }
@keyframes cell { 0% { opacity: .16; } 8% { opacity: .85; } 26% { opacity: .16; } 100% { opacity: .16; } }
.live { animation: live 2.8s ease-in-out infinite; }
@keyframes live { 0%, 100% { opacity: 1; } 50% { opacity: .3; } }
.cur { animation: cur 1.1s steps(1) infinite; }
@keyframes cur { 50% { opacity: 0; } }
.wave { animation: wave 9s linear infinite; }
@keyframes wave { to { transform: translateX(-240px); } }
.type { clip-path: inset(0 100% 0 0); animation: type 1.1s steps(10, end) .25s forwards; }
@keyframes type { to { clip-path: inset(0 -2% 0 0); } }
"""
    deco = ""
    if style == "grid":
        # contribution-style grid: boots in column by column, then a slow diagonal pulse
        rnd = random.Random(11)
        cols, rows, size, gap = 10, 7, 14, 6
        gx, gy = W - 36 - cols * (size + gap) + gap, 62
        cells = []
        for c in range(cols):
            for r in range(rows):
                green = rnd.random() < 0.16
                cells.append(
                    f'<rect class="boot" style="animation-delay:{0.3 + c*0.07 + r*0.02:.2f}s,{2.2 + (c + r)*0.16:.2f}s" '
                    f'x="{gx + c*(size+gap)}" y="{gy + r*(size+gap)}" width="{size}" height="{size}" rx="2" '
                    f'fill="{GREEN if green else TEXT}"/>'
                )
        deco = "".join(cells)
    elif style == "wave":
        # a live monitor: one seamless waveform period, repeated, sliding left
        pts = [(0, 40), (20, 34), (40, 52), (60, 18), (80, 46), (100, 30), (120, 60), (140, 26), (160, 44), (180, 12), (200, 50), (220, 36), (240, 40)]
        d = "M" + " L".join(f"{x} {y}" for x, y in pts)
        d2 = "M" + " L".join(f"{x+240} {y}" for x, y in pts)
        d3 = "M" + " L".join(f"{x+480} {y}" for x, y in pts)
        x0, y0 = W - 36 - 240, 80
        grid = "".join(f'<path d="M0 {y}H240" stroke="{LINE}"/>' for y in (20, 40, 60))
        deco = (f'<clipPath id="wv"><rect x="{x0}" y="{y0-10}" width="240" height="120"/></clipPath>'
                f'<g clip-path="url(#wv)"><g transform="translate({x0},{y0})">{grid}'
                f'<g class="wave"><path d="{d} {d2} {d3}" fill="none" stroke="{TEXT}" stroke-width="1.5" stroke-linejoin="round"/></g>'
                f'<circle cx="238" cy="40" r="3" fill="{GREEN}"/></g></g>'
                f'{text(x0, y0+92, "live  ·  uptime 99.9%", 10, MUTE)}')
    tokens = ["[ germany ]", "[ ibm ]", "[ zerosubnet ]"]
    x, tok = 36, []
    for t in tokens:
        tok.append(text(x, 198, t, 11.5, DIM))
        x += len(t) * 11.5 * 0.6 + 18
    name_cls = "type" if style == "type" else "in i2"
    name_size = 48 if style == "type" else 42
    status = spans(54, 244, [("online", TEXT), ("  ·  shipping daily  ·  open to collaborations ", DIM)], 11.5)
    status = status.replace("</text>", cursor_span() + "</text>")
    body = f"""
<defs><pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".8" fill="{TEXT}" fill-opacity=".10"/></pattern>
<clipPath id="c"><rect width="{W}" height="{H}" rx="10"/></clipPath></defs>
<g clip-path="url(#c)"><rect width="{W}" height="{H}" fill="{BG}"/><rect width="{W}" height="{H}" fill="url(#dots)"/></g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="10" fill="none" stroke="{LINE}"/>
{text(36, 36, "~/niklas-dev", 11.5, MUTE, cls="in i1")}
{text(W-36, 36, "README.md", 11.5, MUTE, anchor="end", cls="in i1")}
{text(34, 98, "Niklas-dev", name_size, TEXT, 700, cls=name_cls, extra=' letter-spacing="-1"')}
{text(36, 130, "security engineer  ·  ai infrastructure  ·  distributed systems", 15, GREEN, cls="in i3")}
{text(36, 160, "Microservices, GPU compute and AI infrastructure that scale, designed and measured.", 12.5, SOFT, cls="in i4")}
<g class="in i5">{''.join(tok)}</g>
<g class="in i6"><circle class="live" cx="42" cy="240" r="3.5" fill="{GREEN}"/>{status}</g>
{deco}
"""
    return svg(W, H, body, css, "Niklas-dev. Security engineer, AI infrastructure, distributed systems. Germany.")


# ----------------------------------------------------------------------- terminal
def terminal() -> str:
    W, pad, top, lh, fs = 900, 26, 70, 24, 13.5
    cw = fs * 0.6
    prompt = [("niklas", GREEN), ("@", DIM), ("dev", GREEN), (":", DIM), ("~", TEXT), (" $ ", GREEN)]
    cmd_x = pad + sum(len(t) for t, _ in prompt) * cw
    seq: list[tuple] = [
        ("cmd", "whoami", 0.4),
        ("out", [("Niklas-dev", TEXT), ("  ·  security software engineer  ·  AI infrastructure  ·  systems that scale", DIM)], 1.2),
        ("cmd", "cat now.txt", 1.9),
        ("out", [("  study   ", MUTE), ("B.Sc. Computer Science / Cyber Security  ·  dual study with IBM", SOFT), ("     2026 → 2029", MUTE)], 3.0),
        ("out", [("  work    ", MUTE), ("Security Software Engineer  ·  ZeroSubnet  ·  security, AI infrastructure, microservices", SOFT)], 3.2),
        ("out", [("  side    ", MUTE), ("post-quantum tooling  ·  Kaggle medals  ·  a homelab that runs itself", SOFT)], 3.4),
        ("cmd", "ls ~/interests", 4.3),
        ("out", [("ai-infrastructure/  gpu-compute/  cuda/  rocm/  kernel-dev/  compute-management/", GREEN)], 5.6),
        ("out", [("scaling-architecture/  system-design/  microservices/  event-driven/  post-quantum-crypto/", GREEN)], 5.8),
        ("prompt", None, 6.4),
    ]
    H = top + lh * len(seq) + 18
    css = """
.fade { opacity: 0; animation: fin .3s ease-out forwards; }
@keyframes fin { to { opacity: 1; } }
.type { clip-path: inset(0 100% 0 0); animation-name: type; animation-timing-function: steps(var(--n), end); animation-fill-mode: forwards; }
@keyframes type { to { clip-path: inset(0 -2% 0 0); } }
.cur { animation: cur 1.1s steps(1) infinite; }
@keyframes cur { 50% { opacity: 0; } }
"""
    rows, y = [], top
    for kind, payload, t in seq:
        if kind == "cmd":
            n = len(payload)
            rows.append(spans(pad, y, prompt, fs, cls="fade", extra=dl(t)))
            rows.append(text(cmd_x, y, payload, fs, TEXT, cls="type",
                             extra=f' style="--n:{n};animation-delay:{t+0.15:.2f}s;animation-duration:{0.07*n:.2f}s"'))
        elif kind == "out":
            rows.append(spans(pad, y, payload, fs, cls="fade", extra=dl(t)))
        else:
            line = spans(pad, y, prompt, fs, cls="fade", extra=dl(t))
            rows.append(line.replace("</text>", cursor_span() + "</text>"))
        y += lh
    body = f"""
{panel(W, H, 10)}
<path d="M.5 42.5H{W-0.5}" stroke="{LINE}"/>
<circle cx="24" cy="21" r="5" fill="none" stroke="{MUTE}"/><circle cx="42" cy="21" r="5" fill="none" stroke="{MUTE}"/><circle cx="60" cy="21" r="5" fill="none" stroke="{MUTE}"/>
{text(W/2, 25.5, "niklas@dev: ~", 12, MUTE, anchor="middle")}
{''.join(rows)}
"""
    return svg(W, H, body, css, "Terminal: whoami, cat now.txt, ls ~/interests")


# ----------------------------------------------------------------- section banners
SECTIONS = [
    ("topics", "01", "WHAT I WORK ON", "nine threads, one engineer"),
    ("work", "02", "SELECTED WORK", "the projects I would show first"),
    ("bench", "03", "ON THE BENCH", "shipped, in progress, or unpublished"),
    ("stack", "04", "STACK", "what I reach for"),
    ("teaching", "05", "TEACHING", "backend development on YouTube"),
    ("activity", "06", "ACTIVITY", "mostly private commits, public graph"),
    ("contact", "07", "CONTACT", "say hi"),
]


def section(key: str, num: str, title: str, sub: str) -> str:
    W, H = 900, 44
    css = """
.rule { stroke-dasharray: 1000; stroke-dashoffset: 1000; animation: rule 1.6s cubic-bezier(.2,.6,.2,1) forwards; }
@keyframes rule { to { stroke-dashoffset: 0; } }
"""
    tw = len(title) * (13 * 0.6 + 1.6)
    x0 = 50 + tw + 18
    x1 = W - 20 - (len(sub) + 3) * 10.5 * 0.6 - 18
    body = f"""
{panel(W, H, 8)}
{text(20, 28, num, 12.5, GREEN, 700)}
{text(50, 28, title, 13, TEXT, 700, extra=' letter-spacing="1.6"')}
<path class="rule" d="M{x0:.0f} 22.5H{x1:.0f}" stroke="{LINE}"/>
{text(W-20, 28, "// " + sub, 10.5, MUTE, anchor="end")}
"""
    return svg(W, H, body, css, f"{num} {title.title()}")


# -------------------------------------------------------------------- topic tiles
TOPICS = [
    ("security", "#", "Security & post-quantum", ["CBOMs, crypto inventory,", "secure services. tessera."]),
    ("aiinfra", "|||", "AI infra & GPU compute", ["CUDA, ROCm, scheduling; model", "workloads run like services."]),
    ("systems", ">_", "System design & scaling", ["Event-driven microservices,", "NATS, Kubernetes, measured."]),
    ("kernel", "0x", "Kernel & low-level", ["Linux kernel development,", "C and Rust close to the metal."]),
    ("ai", "<~>", "AI systems & agents", ["LLM agents wired into real", "systems, not demos."]),
    ("ml", "%", "ML & competitions", ["Kaggle bronze, quantum circuit", "compilation, surrogate models."]),
    ("data", "::", "Data & visualisation", ["11,141 UN speeches on a map,", "836,570 heckles as a graph."]),
    ("product", "$", "Products & SaaS", ["FastLaunchAPI and Dishpad:", "auth, billing, shipping."]),
    ("infra", "##", "Infra, homelab & edge", ["Go panel, Docker, Tailscale;", "ESP32 and Pi on the side."]),
]


def topic_tile(key: str, glyph: str, title: str, lines: list[str], idx: int) -> str:
    W, H = 215, 118
    body = f"""
{panel(W, H, 8)}
{text(16, 27, f"[0{idx+1}]", 10.5, MUTE)}
{text(W-16, 28, glyph, 13, GREEN, 700, anchor="end")}
{text(16, 60, title, 12, TEXT, 700)}
{text(16, 82, lines[0], 10, DIM)}
{text(16, 98, lines[1], 10, DIM)}
"""
    return svg(W, H, body, "", f"{title}: {' '.join(lines)}")


# ------------------------------------------------------------------ project cards
def illo(kind: str) -> str:
    """120x120 monochrome illustration, local coordinates, one slow motion each."""
    if kind == "scan":
        cells = ""
        for r in range(5):
            for c in range(5):
                cells += (f'<rect class="row" style="animation-delay:{0.3 + r*1.0:.1f}s" x="{6 + c*22}" y="{6 + r*22}" '
                          f'width="16" height="16" rx="2" fill="{GREEN if (r*5+c) % 7 == 3 else TEXT}"/>')
        return cells + f'<rect class="scan" x="2" y="4" width="116" height="1.5" fill="{GREEN}"/>'
    if kind == "spark":
        grid = "".join(f'<path d="M4 {y}H116" stroke="{LINE}"/>' for y in (30, 60, 90))
        return (grid + f'<path class="draw" d="M6 92 20 78l12 8 14-22 12 10 16-30 10 14 14-20 12 8" fill="none" '
                f'stroke="{TEXT}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" pathLength="100"/>'
                f'<circle class="end" cx="116" cy="38" r="3" fill="{GREEN}"/>')
    if kind == "bar":
        return (f'{text(4, 22, "6,425 teams", 9, MUTE)}'
                f'<rect x="4" y="34" width="112" height="8" rx="2" fill="{CELL}"/>'
                f'<rect class="fill" x="4" y="34" width="112" height="8" rx="2" fill="{TEXT}"/>'
                f'<rect x="108" y="30" width="2" height="16" fill="{GREEN}"/>'
                f'{text(4, 66, "rank 388", 10.5, TEXT, 700)}'
                f'{text(4, 82, "top 6%  ·  bronze", 9.5, GREEN)}'
                f'{text(4, 104, "0.943 macro AUC", 9.5, DIM)}')
    if kind == "ship":
        return (spans(4, 20, [("$ ", GREEN), ("fastlaunch deploy", TEXT)], 10)
                + text(4, 44, "[" + "░" * 14 + "]", 10, MUTE)
                + '<g class="type" style="--n:14;animation-delay:.6s;animation-duration:1.4s">'
                + text(4, 44, "[" + "█" * 14 + "]", 10, TEXT) + "</g>"
                + text(4, 68, "auth      ok", 9.5, DIM, cls="fade", extra=dl(1.3))
                + text(4, 84, "stripe    ok", 9.5, DIM, cls="fade", extra=dl(1.7))
                + text(4, 100, "docker    ok", 9.5, DIM, cls="fade", extra=dl(2.1))
                + text(4, 114, "live in 10 min", 9.5, GREEN, 700, cls="fade", extra=dl(2.5)))
    if kind == "scatter":
        rnd = random.Random(5)
        groups = [(30, 82, TEXT, .35, 14), (46, 38, TEXT, .6, 12), (88, 50, TEXT, .85, 13), (82, 94, GREEN, .9, 10), (62, 20, TEXT, .45, 6)]
        out = ""
        for i, (cx, cy, col, op, n) in enumerate(groups):
            out += f'<g class="drift" style="animation-delay:{-i*1.7:.1f}s">'
            for _ in range(n):
                dx, dy = rnd.gauss(0, 7), rnd.gauss(0, 7)
                out += f'<circle cx="{cx+dx:.1f}" cy="{cy+dy:.1f}" r="1.9" fill="{col}" fill-opacity="{op}"/>'
            out += "</g>"
        return out
    if kind == "matrix":
        rnd = random.Random(3)
        labels = ["SPD", "AfD", "LNK", "GRN", "CDU"]
        out = ""
        for r in range(5):
            out += text(2, 36 + r*18, labels[r], 7, MUTE)
            for c in range(5):
                if r == c:
                    continue
                v = rnd.random()
                col = GREEN if v > 0.86 else TEXT
                out += (f'<rect class="mx" style="animation-delay:{(r*5+c)*0.11:.2f}s" x="{26 + c*18}" y="{24 + r*18}" '
                        f'width="14" height="14" rx="2" fill="{col}" fill-opacity="{0.12 + v*0.7:.2f}"/>')
        return out + text(26, 14, "who  →  whom", 8, MUTE)
    if kind == "cam":
        corners = "".join(f'<path d="{d}" stroke="{DIM}" stroke-width="1.5" fill="none"/>' for d in
                          ("M6 18V6h12", "M114 18V6h-12", "M6 102v12h12", "M114 102v12h-12"))
        return (corners + f'<circle class="rec" cx="104" cy="16" r="3" fill="{GREEN}"/>'
                f'<g class="track"><rect x="28" y="40" width="44" height="44" rx="2" fill="none" stroke="{GREEN}" stroke-width="1.4" stroke-dasharray="4 3"/>'
                f'{text(28, 36, "cup 0.91", 8.5, GREEN)}</g>'
                f'<rect x="78" y="62" width="30" height="30" rx="2" fill="none" stroke="{TEXT}" stroke-width="1.2" stroke-dasharray="4 3"/>'
                f'{text(78, 58, "key 0.84", 8.5, SOFT)}'
                f'{text(60, 112, "found 2 of 2", 8.5, MUTE, anchor="middle")}')
    if kind == "bus":
        boxes = ""
        for i, name in enumerate(["api", "ingest", "report"]):
            x = 6 + i * 38
            boxes += (f'<rect x="{x}" y="14" width="32" height="18" rx="2" fill="{SURF}" stroke="{LINE}"/>'
                      f'{text(x+16, 26, name, 7.5, DIM, anchor="middle")}'
                      f'<path d="M{x+16} 32V56" stroke="{LINE}"/>')
        return (boxes + f'<path d="M6 56H114" stroke="{TEXT}" stroke-opacity=".5" stroke-width="1.5"/>'
                f'{text(6, 70, "nats", 7.5, MUTE)}'
                f'<circle class="msg" cy="56" r="2.4" fill="{GREEN}"/>'
                f'<circle class="msg" style="animation-delay:-1.6s" cy="56" r="2.4" fill="{GREEN}"/>'
                f'<rect x="6" y="82" width="108" height="18" rx="2" fill="{SURF}" stroke="{LINE}"/>'
                f'{text(60, 94, "kubernetes  ·  3 / 3 ready", 7.5, DIM, anchor="middle")}'
                f'<circle class="led" cx="108" cy="91" r="2.2" fill="{GREEN}"/>'
                f'{text(60, 116, "event-driven  ·  observable", 8, MUTE, anchor="middle")}')
    if kind == "router":
        return (f'<rect x="4" y="50" width="20" height="16" rx="2" fill="{SURF}" stroke="{LINE}"/>{text(14, 61, "q", 8, DIM, anchor="middle")}'
                f'<rect x="40" y="48" width="36" height="20" rx="2" fill="{SURF}" stroke="{TEXT}" stroke-opacity=".6"/>{text(58, 61, "router", 7.5, TEXT, anchor="middle")}'
                f'<rect x="92" y="16" width="26" height="16" rx="2" fill="{SURF}" stroke="{GREEN}"/>{text(105, 27, "nn", 7.5, GREEN, anchor="middle")}'
                f'<rect x="92" y="84" width="26" height="16" rx="2" fill="{SURF}" stroke="{LINE}"/>{text(105, 95, "exact", 7.5, DIM, anchor="middle")}'
                f'<path d="M24 58H40M76 58 92 24M76 58 92 92" stroke="{LINE}" stroke-width="1.2"/>'
                f'<circle r="2.4" fill="{GREEN}"><animateMotion dur="2.4s" repeatCount="indefinite" path="M14 58 H58 L105 24"/></circle>'
                f'<circle r="2.4" fill="{TEXT}"><animateMotion dur="3.6s" begin="1.2s" repeatCount="indefinite" path="M14 58 H58 L105 92"/></circle>'
                f'{text(105, 44, "fast", 7, MUTE, anchor="middle")}{text(105, 112, "when unsure", 7, MUTE, anchor="middle")}')
    if kind == "rack":
        out = ""
        for i, name in enumerate(["caddy", "panel", "immich", "paper", "vault"]):
            y = 10 + i * 21
            out += (f'<rect x="8" y="{y}" width="104" height="15" rx="2" fill="{SURF}" stroke="{LINE}"/>'
                    f'{text(16, y+11, name, 8.5, DIM)}'
                    f'<circle class="led" style="animation-delay:{(i*0.9)%3.4:.1f}s" cx="100" cy="{y+7.5}" r="2.4" fill="{GREEN}"/>')
        return out + text(60, 116, "5 / 5 up", 8.5, MUTE, anchor="middle")
    raise ValueError(kind)


CARD_CSS = """
.row { opacity: .22; animation: row 5.5s ease-in-out infinite; }
@keyframes row { 0% { opacity: .22; } 7% { opacity: 1; } 30% { opacity: .22; } 100% { opacity: .22; } }
.scan { animation: scan 5.5s linear infinite; }
@keyframes scan { 0% { transform: translateY(0); opacity: 0; } 6% { opacity: 1; } 88% { opacity: 1; } 100% { transform: translateY(110px); opacity: 0; } }
.draw { stroke-dasharray: 100; stroke-dashoffset: 100; animation: draw 6s ease-in-out infinite; }
@keyframes draw { 0% { stroke-dashoffset: 100; opacity: 1; } 45% { stroke-dashoffset: 0; } 88% { stroke-dashoffset: 0; opacity: 1; } 100% { stroke-dashoffset: 0; opacity: 0; } }
.end { opacity: 0; animation: end 6s ease-in-out infinite; }
@keyframes end { 0%, 44% { opacity: 0; } 50%, 88% { opacity: 1; } 100% { opacity: 0; } }
.fill { transform-origin: 4px 0; transform: scaleX(0); animation: fill 1.8s cubic-bezier(.2,.7,.2,1) .4s forwards; }
@keyframes fill { to { transform: scaleX(.94); } }
.type { clip-path: inset(0 100% 0 0); animation-name: type; animation-timing-function: steps(var(--n), end); animation-fill-mode: forwards; }
@keyframes type { to { clip-path: inset(0 -2% 0 0); } }
.fade { opacity: 0; animation: fin .4s ease-out forwards; }
@keyframes fin { to { opacity: 1; } }
.drift { animation: drift 9s ease-in-out infinite alternate; }
@keyframes drift { to { transform: translate(3px, -2px); } }
.mx { animation: mx 7s ease-in-out infinite; }
@keyframes mx { 0%, 100% { transform: translate(0,0); } 8% { transform: translate(0,-1.5px); } 16% { transform: translate(0,0); } }
.rec { animation: rec 2.4s ease-in-out infinite; }
@keyframes rec { 0%, 100% { opacity: 1; } 50% { opacity: .25; } }
.track { animation: track 4s ease-in-out infinite alternate; }
@keyframes track { to { transform: translate(5px, 3px); } }
.led { animation: led 3.4s ease-in-out infinite; }
@keyframes led { 0%, 100% { opacity: 1; } 50% { opacity: .2; } }
.msg { animation: msg 3.2s linear infinite; }
@keyframes msg { 0% { transform: translateX(8px); opacity: 0; } 10% { opacity: 1; } 90% { opacity: 1; } 100% { transform: translateX(112px); opacity: 0; } }
"""

CARDS = [
    dict(key="tessera", title="tessera", tag="[public]", tagc=GREEN, illo="scan",
         lines=["Finds the cryptography hiding in a stack:",
                "source, dependency manifests, X.509",
                "certs and live TLS endpoints. Emits a",
                "CBOM with a quantum-risk rating per asset."],
         tags="rust · next.js · cyclonedx · nist pqc",
         stat="> tessera gate . --max-critical 0"),
    dict(key="zerosubnet", title="ZeroSubnet · platform engineering", tag="[work]", tagc=TEXT, illo="bus",
         lines=["Scalable microservices behind a high-",
                "throughput reporting platform: Python",
                "services, event-driven over NATS, run on",
                "Kubernetes with CI/CD and observability."],
         tags="python · nats · kubernetes · observability",
         stat="> microservices · event-driven · since 2024"),
    dict(key="vantage", title="Vantage", tag="[private]", tagc=DIM, illo="spark",
         lines=["Real-time trading intelligence: ingest",
                "workers, TimescaleDB, Redis queues and a",
                "Next.js console. AI signals scored",
                "against outcomes, spend capped per day."],
         tags="fastapi · timescaledb · redis · workers",
         stat="> trust is measured, not assumed"),
    dict(key="hybridsim", title="Hybrid simulation", tag="[research]", tagc=DIM, illo="router",
         lines=["A neural surrogate predicts how a system",
                "evolves; a router hands off to an exact",
                "simulator when confidence drops. 19",
                "domains, one workstation, one GPU."],
         tags="pytorch · surrogate models · compute routing",
         stat="> 58x faster MD · 0.913 AUC on failures"),
    dict(key="rsna", title="Kaggle · RSNA knee MRI", tag="[bronze medal]", tagc=TEXT, illo="bar",
         lines=["Largest medical-imaging competition on",
                "Kaggle, 6,425 teams. Twelve findings per",
                "knee from hundreds of MRI slices; labels",
                "mined from free-text radiology reports."],
         tags="pytorch · coatnet · convnext · solo",
         stat="> rank 388 / 6,425 · 0.943 macro AUC"),
    dict(key="fastlaunchapi", title="FastLaunchAPI", tag="[product]", tagc=TEXT, illo="ship",
         lines=["Production-ready FastAPI starter: auth",
                "with email verification and social login,",
                "Stripe subscriptions, Celery, Docker,",
                "tests. An API ships in minutes."],
         tags="fastapi · postgres · stripe · docker",
         stat="> ~1M views across the launch videos"),
    dict(key="ungdc", title="ungdc-drift", tag="[research]", tagc=DIM, illo="scatter",
         lines=["Every UN General Debate speech since",
                "1946, 11,141 of them, embedded and mapped.",
                "Region explains 59.7% of position;",
                "speech length explains 0.1%."],
         tags="sentence-transformers · umap · pca",
         stat="> 11,141 speeches · 1946 to 2025"),
    dict(key="bundestag", title="bundestag-heckling-network", tag="[research]", tagc=DIM, illo="matrix",
         lines=["Who heckles whom in the Bundestag, 1949",
                "to 2026: 836,570 interruptions as a",
                "directed network, normalised against",
                "expectation, tested against coalitions."],
         tags="postgresql · networkx · louvain · d3",
         stat="> 836,570 heckles · 77 years"),
    dict(key="look-and-mark", title="look-and-mark", tag="[public]", tagc=GREEN, illo="cam",
         lines=["Realtime open-vocabulary detection and",
                "segmentation on a webcam. A Claude agent",
                "finds, marks and counts whatever you ask",
                "for; classes are not fixed upfront."],
         tags="computer vision · claude agent · tool use",
         stat="> webcam in, answers out"),
    dict(key="homelab", title="homelab", tag="[private]", tagc=DIM, illo="rack",
         lines=["Infra and a control panel for a home",
                "server: Go microservices, one Docker stack",
                "per service with CPU priority and memory",
                "limits, Caddy over Tailscale, backups."],
         tags="go · docker · tailscale · caddy · systemd",
         stat="> compute priority per workload"),
]


def card(c: dict) -> str:
    W, H = 440, 200
    desc = "".join(text(20, 60 + i*16, l, 10.5, SOFT) for i, l in enumerate(c["lines"]))
    body = f"""
{panel(W, H, 8)}
{text(20, 32, c["title"], 15, TEXT, 700)}
{text(W-20, 31, c["tag"], 10, c["tagc"], anchor="end")}
{desc}
{text(20, 142, c["tags"], 10, MUTE)}
<path d="M20 160H278" stroke="{LINE}"/>
{text(20, 181, c["stat"], 10.5, GREEN)}
<path d="M296 20V{H-20}" stroke="{LINE}"/>
<g transform="translate(306,36)">{illo(c["illo"])}</g>
"""
    return svg(W, H, body, CARD_CSS, f"{c['title']}: {' '.join(c['lines'])}")


# ----------------------------------------------------------------------- footer
def footer() -> str:
    W, H = 900, 40
    css = """
.cur { animation: cur 1.1s steps(1) infinite; }
@keyframes cur { 50% { opacity: 0; } }
"""
    line = spans(20, 25, [("niklas@dev", GREEN), (":", DIM), ("~", TEXT), (" $ ", GREEN), ("exit ", TEXT)], 12)
    line = line.replace("</text>", cursor_span() + "</text>")
    body = f"""
{panel(W, H, 8)}
{line}
{text(W-20, 25, "// eof  ·  banners are hand-made svg, see tools/", 10.5, MUTE, anchor="end")}
"""
    return svg(W, H, body, css, "exit")


# ----------------------------------------------------------------------- build
def build_all() -> dict[Path, str]:
    files = {OUT / "hero.svg": hero(), OUT / "terminal.svg": terminal(), OUT / "footer.svg": footer()}
    for key, num, title, sub in SECTIONS:
        files[OUT / "sections" / f"{key}.svg"] = section(key, num, title, sub)
    for i, (key, glyph, title, lines) in enumerate(TOPICS):
        files[OUT / "topics" / f"{key}.svg"] = topic_tile(key, glyph, title, lines, i)
    for c in CARDS:
        files[OUT / "cards" / f"{c['key']}.svg"] = card(c)
    return files


def build_options(outdir: Path) -> None:
    """Design variants for comparison: hero styles × backgrounds. Not part of the README."""
    global BG, SURF, LINE
    outdir.mkdir(parents=True, exist_ok=True)
    palettes = {"near-black": ("#090b0d", "#0f1215", "#1c2126"), "pure-black": ("#000000", "#0a0a0a", "#1f1f1f")}
    saved = (BG, SURF, LINE)
    items = []
    for pname, (bg, surf, line) in palettes.items():
        BG, SURF, LINE = bg, surf, line
        for style in ("grid", "wave", "type"):
            name = f"hero-{style}-{pname}.svg"
            (outdir / name).write_text(hero(style), encoding="utf-8", newline="\n")
            items.append((f"Hero · {style} · {pname}", name))
        (outdir / f"card-{pname}.svg").write_text(card(CARDS[0]), encoding="utf-8", newline="\n")
        items.append((f"Card · {pname}", f"card-{pname}.svg"))
    BG, SURF, LINE = saved
    rows = "".join(f'<figure><figcaption>{t}</figcaption><img src="{n}" alt="{t}"></figure>' for t, n in items)
    (outdir / "index.html").write_text(f"""<!doctype html><meta charset="utf-8"><title>Design options</title>
<style>body{{margin:0;padding:32px;background:#0d1117;color:#e6edf3;font:14px -apple-system,Segoe UI,sans-serif}}
figure{{margin:0 0 28px}}figcaption{{margin-bottom:8px;color:#9198a1}}img{{display:block;max-width:900px;width:100%}}
h1{{font-weight:600;font-size:18px}}p{{color:#9198a1;max-width:900px}}</style>
<h1>Design options</h1>
<p>Hero styles: <b>grid</b> (contribution grid that boots in, then a slow diagonal pulse), <b>wave</b> (a live monitor line sliding left), <b>type</b> (typographic, name types in, no decoration). Backgrounds: near-black #090b0d (default) or pure black #000000. Pick one of each; everything else follows.</p>
{rows}""", encoding="utf-8")
    print(f"wrote {len(items)} option images to {outdir}")


def main(argv: list[str]) -> None:
    for sub in ("cards", "topics", "sections"):
        (OUT / sub).mkdir(parents=True, exist_ok=True)
    files = build_all()
    for p, s in files.items():
        p.write_text(s, encoding="utf-8", newline="\n")
    total = sum(len(s.encode()) for s in files.values())
    print(f"wrote {len(files)} files, {total/1024:.0f} KiB total")
    if "--options" in argv:
        build_options(ROOT / ".preview" / "options")


if __name__ == "__main__":
    main(sys.argv[1:])
