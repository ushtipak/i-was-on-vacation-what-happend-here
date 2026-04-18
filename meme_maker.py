#!/usr/bin/env python3
"""
meme_maker.py — imgflip helper for the vacation-backlog meme generator.

Subcommands:
  templates              List top meme templates (ID, name, dimensions)
  create                 Caption a template and save result
  html                   Render output/index.html from saved memes
  clear                  Wipe output/ and start fresh

Env vars required for 'create':
  IMGFLIP_USERNAME
  IMGFLIP_PASSWORD
"""

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "output"
MEMES_FILE  = OUTPUT_DIR / "memes.json"
HTML_FILE   = OUTPUT_DIR / "index.html"
IMGFLIP     = "https://api.imgflip.com"


# ─── imgflip helpers ─────────────────────────────────────────────────────────

_HEADERS = {"User-Agent": "Mozilla/5.0 (vacation-meme-maker/1.0)"}


def _get(url: str) -> dict:
    req = urllib.request.Request(url, headers=_HEADERS)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def fetch_templates(limit: int = 40) -> list:
    payload = _get(f"{IMGFLIP}/get_memes")
    if not payload["success"]:
        die("imgflip returned an error fetching templates")
    return payload["data"]["memes"][:limit]


def caption_image(template_id: str, text0: str, text1: str) -> str:
    username = os.environ.get("IMGFLIP_USERNAME")
    password = os.environ.get("IMGFLIP_PASSWORD")
    if not username or not password:
        die("IMGFLIP_USERNAME and IMGFLIP_PASSWORD must be set")

    body = urllib.parse.urlencode({
        "template_id": template_id,
        "username":    username,
        "password":    password,
        "text0":       text0,
        "text1":       text1,
    }).encode()

    req = urllib.request.Request(f"{IMGFLIP}/caption_image", data=body, headers=_HEADERS, method="POST")
    with urllib.request.urlopen(req) as r:
        payload = json.loads(r.read())

    if not payload["success"]:
        die(f"imgflip error: {payload.get('error_message', 'unknown')}")
    return payload["data"]["url"]


# ─── persistence ─────────────────────────────────────────────────────────────

def load_memes() -> list:
    if MEMES_FILE.exists():
        return json.loads(MEMES_FILE.read_text())
    return []


def append_meme(record: dict) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    memes = load_memes()
    memes.append(record)
    MEMES_FILE.write_text(json.dumps(memes, indent=2))


# ─── HTML generation ─────────────────────────────────────────────────────────

def build_html(memes: list) -> str:
    cards = ""
    for i, m in enumerate(memes, 1):
        event   = m.get("event_name", f"Event #{i}")
        summary = m.get("summary", "")
        top     = m.get("text0", "")
        bot     = m.get("text1", "")
        url     = m["url"]
        tmpl    = m.get("template_name", "")
        cards += f"""
      <div class="card">
        <span class="pill">#{i}</span>
        <h2>{event}</h2>
        <img src="{url}" alt="{event}" loading="lazy">
        {f'<p class="summary">{summary}</p>' if summary else ""}
        {f'<span class="tmpl">template: {tmpl}</span>' if tmpl else ""}
      </div>"""

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>I Was On Vacation — What Happened Here?!</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@400;600&display=swap');
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: #0d0d0d;
      color: #f0f0f0;
      font-family: 'Inter', sans-serif;
      min-height: 100vh;
    }}
    header {{
      text-align: center;
      padding: 3rem 1rem 2rem;
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
      border-bottom: 3px solid #e94560;
    }}
    header h1 {{
      font-family: 'Anton', sans-serif;
      font-size: clamp(2rem, 6vw, 4.5rem);
      letter-spacing: 0.03em;
      color: #fff;
      text-shadow: 3px 3px 0 #e94560;
    }}
    header h2 {{
      font-size: clamp(1rem, 3vw, 1.8rem);
      color: #e94560;
      margin-top: 0.5rem;
      font-weight: 600;
    }}
    .meta {{
      margin-top: 1rem;
      font-size: 0.85rem;
      color: #888;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
      gap: 2rem;
      max-width: 1400px;
      margin: 3rem auto;
      padding: 0 1.5rem 3rem;
    }}
    .card {{
      background: #1a1a1a;
      border: 1px solid #2a2a2a;
      border-radius: 12px;
      overflow: hidden;
      transition: transform 0.2s, box-shadow 0.2s;
      position: relative;
    }}
    .card:hover {{
      transform: translateY(-4px);
      box-shadow: 0 12px 40px rgba(233, 69, 96, 0.2);
    }}
    .pill {{
      display: inline-block;
      background: #e94560;
      color: #fff;
      font-size: 0.7rem;
      font-weight: 700;
      padding: 3px 10px;
      border-radius: 999px;
      margin: 1rem 1rem 0;
      letter-spacing: 0.05em;
    }}
    .card h2 {{
      font-family: 'Anton', sans-serif;
      font-size: 1.3rem;
      padding: 0.5rem 1rem 0.75rem;
      color: #fff;
      letter-spacing: 0.03em;
    }}
    .summary {{
      font-size: 0.88rem;
      color: #ccc;
      padding: 0.75rem 1rem 0.25rem;
      line-height: 1.6;
    }}
    .card img {{
      width: 100%;
      display: block;
    }}
    .captions {{
      padding: 0.75rem 1rem;
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
    }}
    .caption {{
      font-size: 0.82rem;
      font-style: italic;
      color: #bbb;
    }}
    .caption.top::before {{ content: "↑ "; }}
    .caption.bot::before {{ content: "↓ "; }}
    .tmpl {{
      display: block;
      font-size: 0.68rem;
      color: #555;
      padding: 0 1rem 0.75rem;
    }}
    footer {{
      text-align: center;
      padding: 1.5rem;
      font-size: 0.75rem;
      color: #444;
      border-top: 1px solid #1a1a1a;
    }}
  </style>
</head>
<body>
  <header>
    <h1>I Was On Vacation</h1>
    <h2>...What Happened Here?!</h2>
    <p class="meta">{len(memes)} major events &nbsp;·&nbsp; generated {generated_at}</p>
  </header>
  <div class="grid">
    {cards}
  </div>
  <footer>auto-generated by Claude Code &amp; imgflip &nbsp;·&nbsp; you're welcome</footer>
</body>
</html>"""


# ─── subcommands ─────────────────────────────────────────────────────────────

def cmd_templates(args):
    templates = fetch_templates(args.limit)
    print(f"{'ID':<15} {'W':>4} {'H':>4}  NAME")
    print("-" * 60)
    for t in templates:
        print(f"{t['id']:<15} {t['width']:>4} {t['height']:>4}  {t['name']}")


def cmd_create(args):
    url = caption_image(args.id, args.top, args.bottom)
    record = {
        "url":           url,
        "template_id":   args.id,
        "template_name": args.template_name or "",
        "event_name":    args.event or "",
        "summary":       args.summary or "",
        "text0":         args.top,
        "text1":         args.bottom,
        "created_at":    datetime.now().isoformat(),
    }
    append_meme(record)
    print(url)


def cmd_html(args):
    memes = load_memes()
    if not memes:
        die("No memes yet — run 'create' first")
    OUTPUT_DIR.mkdir(exist_ok=True)
    HTML_FILE.write_text(build_html(memes))
    print(f"Saved → {HTML_FILE.resolve()}")


def cmd_clear(args):
    import shutil
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    print("output/ cleared")


# ─── entry point ─────────────────────────────────────────────────────────────

def die(msg: str):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    # templates
    pt = sub.add_parser("templates", help="List top imgflip templates")
    pt.add_argument("--limit", type=int, default=40, help="How many to show (default 40)")

    # create
    pc = sub.add_parser("create", help="Caption a template and save the result")
    pc.add_argument("--id",            required=True,  help="Template ID from 'templates'")
    pc.add_argument("--top",           required=True,  help="Top caption text")
    pc.add_argument("--bottom",        required=True,  help="Bottom caption text")
    pc.add_argument("--event",         default="",     help="Human-readable event name")
    pc.add_argument("--summary",       default="",     help="One-line event summary")
    pc.add_argument("--template-name", default="",     dest="template_name", help="Template name (for the HTML)")

    # html
    sub.add_parser("html", help="Generate output/index.html")

    # clear
    sub.add_parser("clear", help="Delete output/ directory")

    args = p.parse_args()
    {"templates": cmd_templates, "create": cmd_create, "html": cmd_html, "clear": cmd_clear}[args.cmd](args)


if __name__ == "__main__":
    main()
