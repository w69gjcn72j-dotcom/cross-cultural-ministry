#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
add-post.py — put a new essay on yungs.au

    python3 add-post.py ~/Documents/my-essay.docx
    python3 add-post.py ~/Documents/my-essay.docx --lang zh
    python3 add-post.py --check

Takes a Word document (or a .txt / .md file), writes the essay page, and
adds the entry to the right browse list. Then commit and push.

WHAT THE DOCUMENT NEEDS
-----------------------
The first line is the title. Nothing else is required.

A small vocabulary you can type without touching Word's style menu:

    Summary: ...   or  摘要：...     the box under the title
    ## A heading                      a section heading
    ### A small heading               a smaller heading
    > A quotation                     a pulled quotation
    - a point                         a bullet
    1. a point                        a numbered point
    ---                               a dividing rule
    **bold**   *italic*               emphasis

Word's own Heading 1/2/3 styles, bold and italic runs, bullet lists and
tables are all understood too, so a normally-formatted document works
without any of the above.

OPTIONS
-------
    --lang en|zh     force the language (otherwise detected)
    --title "..."    override the title taken from the first line
    --slug my-slug   override the URL slug
    --number 7       override the post number
    --date 2026-08-19
    --blurb "..."    override the one-line summary on the browse page
    --force          overwrite an existing page file
    --check          verify every list entry has a page and vice versa
"""

import argparse
import datetime
import html
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))

CJK = re.compile(r"[㐀-䶿一-鿿豈-﫿]")

SUMMARY_PREFIXES = ("summary:", "summary：", "摘要:", "摘要：", "撮要:", "撮要：")


# ---------------------------------------------------------------- config

def load_site():
    path = os.path.join(HERE, "site.json")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


SITE = load_site()

STRINGS = {
    "en": {
        "summary_label": "Summary",
        "back": "All essays",
        "label_class": "",
        "meta_class": "post-meta",
        "back_class": "backlink",
        "manifest": "manifest.webmanifest",
        "other_index": "index-cn.html",
        "other_label": "中文",
        "other_lang": "zh-Hant",
    },
    "zh": {
        "summary_label": "摘要",
        "back": "返回文章目錄",
        "label_class": " cjk",
        "meta_class": "post-meta cjk",
        "back_class": "backlink cjk",
        "manifest": "manifest-cn.webmanifest",
        "other_index": "index.html",
        "other_label": "English",
        "other_lang": "en",
    },
}

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


def pretty_date(iso, lang):
    y, m, d = (int(x) for x in iso.split("-"))
    if lang == "zh":
        return "%d年%d月%d日" % (y, m, d)
    return "%d %s %d" % (d, MONTHS[m - 1], y)


# ------------------------------------------------------------ reading in

def iter_blocks(doc):
    """Yield ('p', paragraph) and ('table', table) in true document order.
    python-docx exposes paragraphs and tables separately, which loses the
    interleaving; this walks the body XML instead."""
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    body = doc.element.body
    for child in body.iterchildren():
        tag = child.tag.split("}")[-1]
        if tag == "p":
            yield "p", Paragraph(child, doc)
        elif tag == "tbl":
            yield "table", Table(child, doc)


def runs_to_html(para):
    """Paragraph runs -> inline HTML, keeping bold and italic."""
    out = []
    for run in para.runs:
        text = html.escape(run.text)
        if not text:
            continue
        if run.bold:
            text = "<strong>%s</strong>" % text
        if run.italic:
            text = "<em>%s</em>" % text
        out.append(text)
    joined = "".join(out) if out else html.escape(para.text)
    return tidy_inline(joined)


def tidy_inline(s):
    """Typed markup: **bold**, *italic*, [text](link), tidy quotes left alone."""
    s = re.sub(r"\[([^\]\[]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*(?=\S)(.+?)(?<=\S)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*(?=\S)([^*]+?)(?<=\S)\*(?!\*)", r"<em>\1</em>", s)
    # collapse the empty tags Word's run-splitting can produce
    s = re.sub(r"<(strong|em)>\s*</\1>", "", s)
    s = re.sub(r"</(strong|em)>(\s*)<\1>", r"\2", s)
    return s.strip()


def read_blocks(path):
    """Return a list of (kind, payload) blocks from .docx / .md / .txt.

    kind is one of: para, h2, h3, quote, bullet, number, rule, table
    """
    ext = os.path.splitext(path)[1].lower()
    if ext in (".txt", ".md", ".markdown"):
        return read_plain(path)
    if ext != ".docx":
        sys.exit("I can read .docx, .md or .txt — not %s" % (ext or "that"))
    return read_docx(path)


def read_plain(path):
    with open(path, encoding="utf-8-sig") as fh:
        lines = fh.read().splitlines()
    blocks = []
    buf = []

    def flush():
        if buf:
            blocks.append(("para", tidy_inline(html.escape(" ".join(buf)))))
            buf.clear()

    in_sources = False
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        i += 1

        if not line.strip():
            flush()
            continue

        # markdown table: a header row followed by a |---|---| divider
        if line.lstrip().startswith("|") and i < len(lines) \
                and re.fullmatch(r"\s*\|[\s:|-]+\|\s*", lines[i] or ""):
            flush()
            rows = [split_md_row(line)]
            i += 1                                   # skip the divider
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append(split_md_row(lines[i]))
                i += 1
            blocks.append(("table", [[tidy_inline(html.escape(c)) for c in r]
                                     for r in rows]))
            continue

        # [figure: path | caption]   [figure-wide: path | caption]
        m = re.match(r"^\[figure(-wide)?:\s*(.+?)\s*(?:\|\s*(.*?))?\]$", line.strip())
        if m:
            flush()
            blocks.append(("figure", {
                "src": m.group(2),
                "caption": tidy_inline(html.escape(m.group(3) or "")),
                "wide": bool(m.group(1)),
            }))
            continue

        # [video: path.mp4 | poster.jpg]  — renders a placeholder if absent
        m = re.match(r"^\[video:\s*(.+?)\s*(?:\|\s*(.*?))?\]$", line.strip())
        if m:
            flush()
            blocks.append(("video", {"src": m.group(1), "poster": m.group(2) or ""}))
            continue

        # [youtube: <id or url> | caption]  — click-to-play, no tracking until clicked
        m = re.match(r"^\[youtube:\s*(.+?)\s*(?:\|\s*(.*?))?\]$", line.strip())
        if m:
            flush()
            blocks.append(("youtube", {
                "id": youtube_id(m.group(1)),
                "caption": tidy_inline(html.escape(m.group(2) or "")),
            }))
            continue

        # [note] a short editorial note, set apart from the argument
        m = re.match(r"^\[note\]\s*(.*)$", line.strip())
        if m:
            flush()
            blocks.append(("note", tidy_inline(html.escape(m.group(1)))))
            continue

        # [sources] — the bullets that follow become a hanging-indent list
        if line.strip() == "[sources]":
            flush()
            in_sources = True
            continue

        kind, payload = classify(line)
        if kind == "bullet" and in_sources:
            flush()
            blocks.append(("source", tidy_inline(html.escape(payload))))
            continue
        if kind == "para":
            in_sources = False
            buf.append(line.strip())
        else:
            flush()
            blocks.append((kind, tidy_inline(html.escape(payload))
                           if kind != "rule" else ""))
    flush()
    return blocks


def youtube_id(s):
    """Accept a bare id, a watch URL, a youtu.be link or an embed URL."""
    s = s.strip()
    m = re.search(r"(?:v=|youtu\.be/|/embed/|/shorts/)([A-Za-z0-9_-]{11})", s)
    if m:
        return m.group(1)
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", s):
        return s
    sys.exit("That doesn't look like a YouTube video id or link: %r" % s)


def split_md_row(line):
    cells = line.strip().strip("|").split("|")
    return [c.strip() for c in cells]


def read_docx(path):
    try:
        import docx  # python-docx
    except ImportError:
        sys.exit("python-docx is missing.  pip install python-docx")

    doc = docx.Document(path)
    blocks = []

    for kind, item in iter_blocks(doc):
        if kind == "table":
            rows = []
            for r in item.rows:
                rows.append([tidy_inline(html.escape(c.text.strip()))
                             for c in r.cells])
            if any(any(c for c in row) for row in rows):
                blocks.append(("table", rows))
            continue

        para = item
        text = para.text.strip()
        if not text:
            continue

        style = (para.style.name or "").lower()
        inline = runs_to_html(para)

        # Word's own styles first
        if style.startswith("heading 1") or style.startswith("title"):
            blocks.append(("h2", inline))
            continue
        if style.startswith("heading 2"):
            blocks.append(("h2", inline))
            continue
        if style.startswith("heading 3") or style.startswith("heading 4"):
            blocks.append(("h3", inline))
            continue
        if style.startswith("quote") or style.startswith("intense quote"):
            blocks.append(("quote", inline))
            continue
        if "list number" in style:
            blocks.append(("number", strip_marker(inline)))
            continue
        if "list" in style:            # List Paragraph, List Bullet, ...
            blocks.append(("bullet", strip_marker(inline)))
            continue

        # then the typed vocabulary
        typed_kind, payload = classify(text)
        if typed_kind != "para":
            if typed_kind == "rule":
                blocks.append(("rule", ""))
            else:
                # re-apply the run formatting where we can, else escape plain
                blocks.append((typed_kind, tidy_inline(html.escape(payload))))
            continue

        blocks.append(("para", inline))

    return blocks


def strip_marker(s):
    return re.sub(r"^\s*(?:[-*•·–]|\d+[.)])\s+", "", s)


def classify(line):
    """Typed-vocabulary classifier. Returns (kind, payload)."""
    s = line.strip()
    if re.fullmatch(r"(-{3,}|_{3,}|\*{3,}|—{2,})", s):
        return "rule", ""
    m = re.match(r"^(#{2,4})\s+(.*)$", s)
    if m:
        return ("h2" if len(m.group(1)) == 2 else "h3"), m.group(2).strip()
    if s.startswith(">"):
        return "quote", s.lstrip("> ").strip()
    if re.match(r"^\s*[-*•·]\s+", s):
        return "bullet", strip_marker(s)
    if re.match(r"^\s*\d+[.)]\s+", s):
        return "number", strip_marker(s)
    return "para", s


# ------------------------------------------------------------- assembling

def detect_lang(blocks):
    text = " ".join(b for k, b in blocks if isinstance(b, str))
    cjk = len(CJK.findall(text))
    letters = len(re.findall(r"[A-Za-z]", text))
    return "zh" if cjk > max(20, letters * 0.15) else "en"


def take_title(blocks):
    for i, (kind, payload) in enumerate(blocks):
        if kind in ("para", "h2", "h3") and isinstance(payload, str) and payload:
            title = html.unescape(re.sub(r"<[^>]+>", "", payload)).strip()
            return title, blocks[:i] + blocks[i + 1:]
    sys.exit("That document looks empty — I couldn't find a title line.")


def take_summary(blocks):
    for i, (kind, payload) in enumerate(blocks):
        if kind != "para" or not isinstance(payload, str):
            continue
        plain = html.unescape(re.sub(r"<[^>]+>", "", payload)).strip()
        low = plain.lower()
        for pref in SUMMARY_PREFIXES:
            if low.startswith(pref):
                body = plain[len(pref):].strip()
                return body, blocks[:i] + blocks[i + 1:]
        break      # only look at the first paragraph
    return "", blocks


def slugify(title, fallback):
    s = unicodedata.normalize("NFKD", title)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()
    s = re.sub(r"-{2,}", "-", s)
    words = [w for w in s.split("-") if w]
    s = "-".join(words[:8])
    return s or fallback


def render_body(blocks):
    out = []
    i = 0
    while i < len(blocks):
        kind, payload = blocks[i]

        if kind in ("bullet", "number"):
            tag = "ul" if kind == "bullet" else "ol"
            items = []
            while i < len(blocks) and blocks[i][0] == kind:
                items.append("    <li>%s</li>" % blocks[i][1])
                i += 1
            out.append("  <%s>\n%s\n  </%s>" % (tag, "\n".join(items), tag))
            continue

        if kind == "source":
            items = []
            while i < len(blocks) and blocks[i][0] == "source":
                items.append("    <li>%s</li>" % blocks[i][1])
                i += 1
            out.append('  <ul class="sources">\n%s\n  </ul>' % "\n".join(items))
            continue

        if kind == "figure":
            cls = ' class="wide"' if payload.get("wide") else ""
            src = payload["src"]
            cap = payload.get("caption") or ""
            inner = ""
            local = os.path.join(HERE, src)
            if src.lower().endswith(".svg") and os.path.exists(local):
                # inline the SVG so it inherits the page's colours
                with open(local, encoding="utf-8") as fh:
                    inner = fh.read().strip()
                inner = re.sub(r"<\?xml.*?\?>\s*", "", inner, flags=re.S)
            else:
                inner = '<img src="%s" alt="%s" loading="lazy">' % (
                    html.escape(src, quote=True),
                    re.sub(r"<[^>]+>", "", cap) or "Figure",
                )
            capline = ""
            if cap:
                capline = '\n    <figcaption>%s</figcaption>' % cap
            out.append("  <figure%s>\n    %s%s\n  </figure>" % (cls, inner, capline))
            i += 1
            continue

        if kind == "video":
            src = payload["src"]
            poster = payload.get("poster") or ""
            if os.path.exists(os.path.join(HERE, src)):
                attrs = ' poster="%s"' % html.escape(poster, quote=True) if poster else ""
                out.append(
                    '  <div class="videoslot">\n'
                    '    <video controls preload="metadata"%s>\n'
                    '      <source src="%s" type="video/mp4">\n'
                    '      Your browser cannot play this video.\n'
                    '    </video>\n'
                    '  </div>' % (attrs, html.escape(src, quote=True))
                )
            else:
                out.append(VIDEO_PLACEHOLDER.format(src=html.escape(src, quote=True)))
            i += 1
            continue

        if kind == "youtube":
            out.append(YOUTUBE_BLOCK.format(
                id=payload["id"],
                caption=('\n    <figcaption>%s</figcaption>' % payload["caption"])
                        if payload["caption"] else "",
            ))
            i += 1
            continue

        if kind == "note":
            out.append('  <div class="note">%s</div>' % payload)
            i += 1
            continue

        if kind == "quote":
            paras = []
            while i < len(blocks) and blocks[i][0] == "quote":
                paras.append("    <p>%s</p>" % blocks[i][1])
                i += 1
            out.append("  <blockquote>\n%s\n  </blockquote>" % "\n".join(paras))
            continue

        if kind == "table":
            rows = payload
            head, body = rows[0], rows[1:]
            th = "".join("<th>%s</th>" % c for c in head)
            trs = "".join(
                "\n      <tr>%s</tr>" % "".join("<td>%s</td>" % c for c in r)
                for r in body
            )
            out.append(
                "  <table>\n    <thead><tr>%s</tr></thead>\n    <tbody>%s\n    </tbody>\n  </table>"
                % (th, trs)
            )
            i += 1
            continue

        if kind == "rule":
            out.append("  <hr>")
        elif kind == "h2":
            out.append("  <h2>%s</h2>" % payload)
        elif kind == "h3":
            out.append("  <h3>%s</h3>" % payload)
        else:
            out.append("  <p>%s</p>" % payload)
        i += 1

    return "\n\n".join(out)


VIDEO_PLACEHOLDER = """  <div class="videoslot">
    <div class="placeholder">
      <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <rect x="4" y="14" width="42" height="36" rx="6" stroke="#C96F4C" stroke-width="3"/>
        <path d="M46 30l13-8v20l-13-8z" stroke="#E8B08C" stroke-width="3" stroke-linejoin="round"/>
      </svg>
      <div>The introduction video goes here.<br>
      Drop the file in as <code>{src}</code> and it will appear.</div>
    </div>
  </div>"""


YOUTUBE_BLOCK = """  <figure class="ytwrap">
    <div class="yt" data-id="{id}">
      <button type="button" class="yt-cover" aria-label="Play the video">
        <img src="https://i.ytimg.com/vi/{id}/hqdefault.jpg" alt="" loading="lazy" decoding="async">
        <span class="yt-play" aria-hidden="true">
          <svg viewBox="0 0 68 48"><path d="M66.5 7.7a8.6 8.6 0 0 0-6-6C55.2 0 34 0 34 0S12.8 0 7.5 1.7a8.6 8.6 0 0 0-6 6A90 90 0 0 0 0 24a90 90 0 0 0 1.5 16.3 8.6 8.6 0 0 0 6 6C12.8 48 34 48 34 48s21.2 0 26.5-1.7a8.6 8.6 0 0 0 6-6A90 90 0 0 0 68 24a90 90 0 0 0-1.5-16.3z" fill="#C96F4C"/><path d="M27 34l18-10-18-10z" fill="#06201F"/></svg>
        </span>
      </button>
    </div>
    <noscript>
      <p><a href="https://www.youtube.com/watch?v={id}">Watch the video on YouTube</a></p>
    </noscript>{caption}
  </figure>
  <script>
  (function () {{
    var box = document.currentScript.previousElementSibling.querySelector(".yt");
    box.querySelector(".yt-cover").addEventListener("click", function () {{
      var f = document.createElement("iframe");
      f.src = "https://www.youtube-nocookie.com/embed/" + box.dataset.id +
              "?autoplay=1&rel=0&modestbranding=1";
      f.title = "Video";
      f.allow = "accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture";
      f.allowFullscreen = true;
      f.setAttribute("frameborder", "0");
      box.replaceChildren(f);
    }});
  }})();
  </script>"""


PAGE = """<!DOCTYPE html>
<html lang="{htmllang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title_esc} — {site_title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#06201F">
<meta property="og:title" content="{title_esc}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="{base}/{filename}">
<meta property="og:image" content="{base}/icons/icon-512.png">
<meta property="article:published_time" content="{date}">
<link rel="canonical" href="{base}/{filename}">
<link rel="icon" href="favicon.ico" sizes="any">
<link rel="icon" type="image/png" href="icons/icon-192.png">
<link rel="apple-touch-icon" href="icons/icon-180.png">
<link rel="manifest" href="{manifest}">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Inter+Tight:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
</head>
<body>

<header class="masthead">
  <div class="masthead-inner">
    <svg class="mark" viewBox="0 0 1024 1024" role="img" aria-label="{mark_alt}">
      <rect width="1024" height="1024" rx="190" fill="#06201F"/>
      <line x1="152" y1="690" x2="872" y2="690" stroke="#92705E" stroke-width="16"/>
      <circle cx="410" cy="540" r="205" fill="none" stroke="#C96F4C" stroke-width="20"/>
      <circle cx="614" cy="540" r="205" fill="none" stroke="#C96F4C" stroke-width="20"/>
      <path d="M512 352V792M438 470H586" stroke="#E8B08C" stroke-width="23" stroke-linecap="round"/>
    </svg>
    <div>
      <h1><a href="{index}" style="color:inherit;text-decoration:none">{site_title}</a></h1>
      <p class="byline{label_class}">{author}</p>
    </div>
  </div>
</header>

<main class="wrap narrow">

  <a class="{back_class}" href="{index}">&larr; {back}</a>

  <div class="essay-head">
    <div class="{meta_class}">
      <span class="num">{num}</span>
      <span>{date_pretty}</span>
    </div>
    <h1>{title_esc}</h1>
{summary_block}  </div>

  <article class="essay">
{body}
  </article>

</main>

<footer class="footer">
  <div class="footer-inner">
    <p>{footer}</p>
    <p><a href="{index}">{back}</a></p>
  </div>
</footer>

</body>
</html>
"""

SUMMARY_BLOCK = """    <div class="summary">
      <span class="label{label_class}">{summary_label}</span>
      {summary}
    </div>
"""


# ---------------------------------------------------------------- indexes

POSTS_RE = re.compile(r"(const POSTS = \[)(.*?)(\n\];)", re.S)


def read_posts(index_path):
    with open(index_path, encoding="utf-8") as fh:
        source = fh.read()
    m = POSTS_RE.search(source)
    if not m:
        sys.exit("Couldn't find the POSTS list in %s" % os.path.basename(index_path))
    inner = m.group(2)
    posts = []
    for entry in re.finditer(r"\{(.*?)\}", inner, re.S):
        fields = dict(re.findall(r'(\w+)\s*:\s*"(.*?)"', entry.group(1)))
        n = re.search(r"\bn\s*:\s*(\d+)", entry.group(1))
        if n:
            fields["n"] = int(n.group(1))
        posts.append(fields)
    return source, m, posts


def js_str(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def insert_post(index_path, entry):
    source, m, posts = read_posts(index_path)
    block = (
        '\n  {\n'
        '    n: %d,\n'
        '    date: "%s",\n'
        '    slug: "%s",\n'
        '    title: "%s",\n'
        '    blurb: "%s"\n'
        '  }' % (entry["n"], entry["date"], entry["slug"],
                 js_str(entry["title"]), js_str(entry["blurb"]))
    )
    existing = m.group(2).strip()
    inner = block + (",\n  " + existing.lstrip() if existing else "")
    new_source = source[:m.start()] + m.group(1) + inner + m.group(3) + source[m.end():]
    with open(index_path, "w", encoding="utf-8") as fh:
        fh.write(new_source)


# ------------------------------------------------------------------ check

def check():
    problems = []
    counts = {}
    seen_files = set()

    for lang in ("en", "zh"):
        index_path = os.path.join(HERE, SITE["index"]["en" if lang == "en" else "zh"])
        if not os.path.exists(index_path):
            problems.append("missing index: %s" % os.path.basename(index_path))
            continue
        _, _, posts = read_posts(index_path)
        counts[lang] = len(posts)
        numbers = []
        for p in posts:
            slug = p.get("slug", "")
            numbers.append(p.get("n"))
            page = os.path.join(HERE, slug)
            if not slug:
                problems.append("%s: an entry has no slug" % os.path.basename(index_path))
            elif not os.path.exists(page):
                problems.append("%s: entry %s points at %s, which isn't there"
                                % (os.path.basename(index_path), p.get("n"), slug))
            else:
                seen_files.add(slug)
            if not p.get("title"):
                problems.append("%s: entry %s has no title"
                                % (os.path.basename(index_path), p.get("n")))
            date = p.get("date", "")
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date or ""):
                problems.append("%s: entry %s has a odd date %r"
                                % (os.path.basename(index_path), p.get("n"), date))
        dupes = {n for n in numbers if numbers.count(n) > 1}
        if dupes:
            problems.append("%s: repeated post numbers %s"
                            % (os.path.basename(index_path), sorted(dupes)))

    # any page file not listed anywhere?
    for name in sorted(os.listdir(HERE)):
        if re.fullmatch(r"\d{3}-.+\.html", name) and name not in seen_files:
            problems.append("%s is on disk but not in any browse list" % name)

    # supporting files
    for required in ("style.css", "site.json", "manifest.webmanifest",
                     "manifest-cn.webmanifest", "CNAME",
                     "icons/icon-192.png", "icons/icon-512.png"):
        if not os.path.exists(os.path.join(HERE, required)):
            problems.append("missing %s" % required)

    page_files = len([n for n in os.listdir(HERE) if re.fullmatch(r"\d{3}-.+\.html", n)])

    if problems:
        print("PROBLEMS")
        for p in problems:
            print("  - " + p)
        return 1

    print("OK — %d English, %d Chinese, %d page files, all matched"
          % (counts.get("en", 0), counts.get("zh", 0), page_files))
    return 0


# ------------------------------------------------------------------- main

def next_number(lang):
    index_path = os.path.join(HERE, SITE["index"]["en" if lang == "en" else "zh"])
    _, _, posts = read_posts(index_path)
    ns = [p["n"] for p in posts if isinstance(p.get("n"), int)]
    return (max(ns) + 1) if ns else 1


def number_for_title(lang, title):
    """If this title is already published, re-use its number — so running the
    script again on a revised document updates that post instead of adding a
    second copy of it."""
    index_path = os.path.join(HERE, SITE["index"]["en" if lang == "en" else "zh"])
    _, _, posts = read_posts(index_path)
    want = " ".join(title.split()).lower()
    for p in posts:
        if " ".join(p.get("title", "").split()).lower() == want:
            n = p.get("n")
            if isinstance(n, int):
                return n
    return None


def english_slug_for(number):
    """If the English post with this number exists, pair the Chinese one to it."""
    _, _, posts = read_posts(os.path.join(HERE, SITE["index"]["en"]))
    for p in posts:
        if p.get("n") == number and p.get("slug"):
            return re.sub(r"^\d{3}-|\.html$", "", p["slug"])
    return None


def make_blurb(summary, blocks, lang):
    text = summary
    if not text:
        for kind, payload in blocks:
            if kind == "para" and isinstance(payload, str):
                text = html.unescape(re.sub(r"<[^>]+>", "", payload))
                break
    text = " ".join(text.split())
    limit = 90 if lang == "zh" else 200
    if len(text) > limit:
        cut = text[:limit]
        stop = max(cut.rfind("。"), cut.rfind(". "))
        if stop > limit * 0.45:
            text = cut[:stop + 1].rstrip()
        else:
            # back off to a word boundary and trail off, never mid-clause
            text = cut.rsplit(" ", 1)[0].rstrip(" ,;:—–-") + "…"
    return text.strip()


def main():
    ap = argparse.ArgumentParser(add_help=True, description="Add an essay to yungs.au")
    ap.add_argument("document", nargs="?", help=".docx, .md or .txt")
    ap.add_argument("--lang", choices=["en", "zh"])
    ap.add_argument("--title")
    ap.add_argument("--slug")
    ap.add_argument("--number", type=int)
    ap.add_argument("--date")
    ap.add_argument("--blurb")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    if args.check:
        sys.exit(check())

    if not args.document:
        ap.error("give me a document, or --check")
    if not os.path.exists(args.document):
        sys.exit("Can't find %s" % args.document)

    blocks = read_blocks(args.document)
    if not blocks:
        sys.exit("That document came out empty.")

    title, blocks = take_title(blocks)
    if args.title:
        title = args.title
    summary, blocks = take_summary(blocks)

    lang = args.lang or detect_lang(blocks + [("para", title)])
    s = STRINGS[lang]

    number = args.number or number_for_title(lang, title) or next_number(lang)
    date = args.date or datetime.date.today().isoformat()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        sys.exit("--date wants YYYY-MM-DD")

    if args.slug:
        base_slug = args.slug
    elif lang == "zh":
        base_slug = english_slug_for(number) or slugify(title, "post-%03d" % number)
    else:
        base_slug = slugify(title, "post-%03d" % number)

    filename = "%03d-%s%s.html" % (number, base_slug, SITE["suffix"]["en" if lang == "en" else "zh"])
    page_path = os.path.join(HERE, filename)
    if os.path.exists(page_path) and not args.force:
        sys.exit("%s already exists. Use --force to overwrite it." % filename)

    blurb = args.blurb or make_blurb(summary, blocks, lang)

    summary_block = ""
    if summary:
        summary_block = SUMMARY_BLOCK.format(
            label_class=s["label_class"],
            summary_label=s["summary_label"],
            summary=html.escape(summary),
        )

    page = PAGE.format(
        htmllang="zh-Hant" if lang == "zh" else "en",
        title_esc=html.escape(title),
        site_title=html.escape(SITE["title"]["zh" if lang == "zh" else "en"]),
        desc=html.escape(blurb or title, quote=True),
        base=SITE["base_url"],
        filename=filename,
        date=date,
        date_pretty=pretty_date(date, lang),
        num="%03d" % number,
        manifest=s["manifest"],
        index=SITE["index"]["zh" if lang == "zh" else "en"],
        author=html.escape(SITE["author"]["zh" if lang == "zh" else "en"]),
        footer=html.escape(SITE["footer"]["zh" if lang == "zh" else "en"]),
        back=s["back"],
        back_class=s["back_class"],
        meta_class=s["meta_class"],
        label_class=s["label_class"],
        mark_alt=("兩個相交的圓，十架立於交疊之處" if lang == "zh"
                  else "Two overlapping circles with a cross standing in the overlap"),
        summary_block=summary_block,
        body=render_body(blocks),
    )

    with open(page_path, "w", encoding="utf-8") as fh:
        fh.write(page)

    index_path = os.path.join(HERE, SITE["index"]["zh" if lang == "zh" else "en"])
    rewrite_without(index_path, filename)   # so --force really replaces
    insert_post(index_path, {
        "n": number, "date": date, "slug": filename,
        "title": title, "blurb": blurb,
    })

    print("Wrote   %s" % filename)
    print("Listed  in %s as post %03d" % (os.path.basename(index_path), number))
    print("Title   %s" % title)
    if summary:
        print("Summary %s" % summary[:70] + ("…" if len(summary) > 70 else ""))
    print()
    print("Now:  git add -A && git commit -m \"%s\" && git push" % title)


def rewrite_without(index_path, slug):
    """Drop an existing entry for this slug, so --force really replaces it."""
    source, m, _ = read_posts(index_path)
    inner = m.group(2)
    kept = []
    for entry in re.finditer(r"\{.*?\}", inner, re.S):
        if '"%s"' % slug not in entry.group(0):
            kept.append(entry.group(0))
    new_inner = ""
    if kept:
        new_inner = "\n  " + ",\n  ".join(k.strip() for k in kept)
    new_source = source[:m.start()] + m.group(1) + new_inner + m.group(3) + source[m.end():]
    with open(index_path, "w", encoding="utf-8") as fh:
        fh.write(new_source)


if __name__ == "__main__":
    main()
