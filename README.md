# Cross-Cultural Ministry — yungs.au

Essays by Rev David Yung 翁沛偉牧師, in English and Chinese.
Plain HTML on GitHub Pages. No build step, no dependencies at read time.

---

## Adding an essay

Write it in Word. The **first line is the title**. Then:

```
python3 add-post.py my-essay.docx
python3 add-post.py --check
git add -A && git commit -m "Title of the essay" && git push
```

Live in about a minute.

The language is detected from the document, so a Chinese essay goes to the
Chinese list without being told. Give a Chinese version the **same post
number** as its English original and the two are paired automatically:

```
python3 add-post.py my-essay-chinese.docx --number 3
```

Run the script again on a revised document and it **updates that post in
place** rather than adding a second copy — it matches on the title. Add
`--force` to let it overwrite the page file.

### What the script understands

Nothing but the title is required. These are available if you want them,
and none needs Word's style menu:

| You type | You get |
|---|---|
| `Summary: …` or `摘要：…` | the box under the title |
| `## A heading` | a section heading |
| `### A small heading` | a smaller heading |
| `> A quotation` | a pulled quotation |
| `- a point` | a bullet |
| `1. a point` | a numbered point |
| `---` | a dividing rule |
| `**bold**` `*italic*` | emphasis |
| `[words](002-something.html)` | a link |
| `\| a \| b \|` with a `\|---\|---\|` row under it | a table |
| `[figure: figures/x.svg \| Caption]` | a figure; SVGs are inlined so they pick up the site's colours |
| `[figure-wide: … ]` | the same, running wider than the reading measure |
| `[youtube: <id or link> \| Caption]` | a YouTube video, click-to-play |
| `[video: media/x.mp4]` | a self-hosted video, or a tidy placeholder if the file isn't there yet |
| `[note] …` | a boxed aside, set apart from the argument |
| `[sources]` | the bullets after it become a reference list with hanging indents |

Word's own Heading 1/2/3 styles, bold and italic, bullet lists and tables
all work too, so a normally-formatted document needs none of the above.

### Other options

```
--lang en|zh     force the language
--title "..."    override the title
--slug my-slug   override the URL
--number 7       override the post number
--date 2026-08-19
--blurb "..."    override the browse-page one-liner
--force          overwrite an existing page
--check          verify the lists and the files agree
```

`--check` is the discipline: run it before every push. It confirms every
list entry has a page, every page is listed, no repeated numbers, and the
supporting files are all present.

---

## Putting it live (once) — pick one route

| You have | Read |
|---|---|
| **GitHub Desktop** | `GITHUB-DESKTOP.md` — recommended |
| nothing installed | `UPLOAD-WITHOUT-TERMINAL.md` — drag and drop in a browser |
| the `gh` CLI | run `bash setup-github.sh` — does it all |
| git, but not `gh` | `PUSHING-BY-HAND.md` |

The steps below are the underlying shape of it, whichever route you take.

## The steps themselves

1. **New repo** on GitHub called `cross-cultural-ministry`, **public**.
   Unzip this into your local clone and push.
2. **Settings → Pages** → Deploy from a branch → `main` → `/ (root)`.
3. **Settings → Pages → Custom domain** → `yungs.au`.
   (The `CNAME` file in this repo already says so.)
4. **DNS at Squarespace** — four A records on the apex:

   ```
   185.199.108.153
   185.199.109.153
   185.199.110.153
   185.199.111.153
   ```

   and a CNAME for `www` → `<your-github-username>.github.io`
5. Tick **Enforce HTTPS** once it appears (can take up to an hour).

Your study libraries are untouched by any of this. They stay on their
`github.io` addresses and the Saturday task carries on as normal.

---

## What's in here

```
index.html            English browse page — holds const POSTS = [...]
index-cn.html         Chinese browse page — holds its own const POSTS
00N-*.html            one file per essay
404.html
style.css             the whole design, in one file
add-post.py           the converter
site.json             titles, author, domain — change them here
manifest.webmanifest  home-screen install, English
manifest-cn.webmanifest        …and Chinese
icons/                the mark, at every size
figures/              diagrams, as SVG
media/                the introduction video goes here
favicon.ico
tools/gen_icons.py    redraws the icons; only needed if the mark changes
drafts/               the source files every published essay was made from
CNAME                 yungs.au
.nojekyll             stops GitHub trying to build this as a Jekyll site
```

Every published essay has its source in `drafts/`. Edit the source, re-run
`add-post.py … --force`, and the page is rebuilt in place — that is the way
to revise a piece, rather than editing the HTML.

`add-post.py` needs `python-docx` for Word files:
`pip3 install python-docx`

---

## A standing decision about names

The essays describe a real congregation and do not name it, and identifying
details about individuals have been generalised. Two source citations are
deliberately incomplete for the same reason — the parish history and the
consultants' reports. If that ever changes, it should change on purpose.

Note that the site carries the author's name, so this is a courtesy screen
rather than true anonymity: a determined reader can work out which parish is
meant. It raises the cost of recognising yourself in an unflattering
paragraph; it does not make it impossible.

## The mark

Two overlapping circles — two cultures — with the cross standing in the
overlap, its foot crossing the horizon.

## Changing the look

Everything visual lives in `style.css`, and the colours are the handful of
custom properties at the top. Change `--clay` and the whole site changes
with it.
