# Cross-Cultural Ministry — yungs.au

Essays by Rev David Yung 翁沛偉牧師, in English and Chinese.
Plain HTML on GitHub Pages. No build step, no dependencies at read time.

---

## Adding an essay

**No Terminal:** double-click `tools/convert.html`, drag in the Word file and
`essays.html`, download the two files it gives you, and commit in GitHub
Desktop. Full instructions in `ADDING-ESSAYS.md`. This is the everyday route.

**With Terminal**, `add-post.py` does the same and a little more — figures,
videos, reference lists, and `--check`. Write it in Word. The **first line is
the title**. Then:

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
index.html            the title page — the "Not Young, but Yung" hero, then
                      the three doors and the links list. SELF-CONTAINED:
                      its own inline CSS and JS, its own palette (ink and
                      gold, EB Garamond), and it does NOT use style.css.
index-cn.html         the Chinese title page, same hero
essays.html           English browse page — holds const POSTS = [...]
essays-cn.html        Chinese browse page — holds its own const POSTS
00N-*.html            one file per essay
404.html
style.css             the whole design, in one file
add-post.py           the converter
site.json             titles, wordmark, author, domain — change them here
manifest.webmanifest  home-screen install, English
manifest-cn.webmanifest        …and Chinese
icons/                the mark, at every size
figures/              diagrams, as SVG
media/                the introduction video goes here
favicon.ico
tools/convert.html    the browser converter — double-click it, no install
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

## The wordmark

Every inner page carries the same name as the title page — *Not Young, but
Yung* in English, 翁 & Jung in Chinese — so the link back to home looks like
home. It lives in `site.json` under `wordmark` and `tagline`, as small
fragments of HTML, and is styled by the `.wm-*` rules at the end of
`style.css`.

Change it there and re-run `add-post.py … --force` on each essay to rebuild
the mastheads. The two browse pages, `essays.html` and `essays-cn.html`, hold
their own copy — edit those by hand to match.

## The title page

`index.html` carries the name-constellation hero — 32 forms of 翁 across the
world's scripts. Three things control it, all near the bottom of the file:

- `NAMES` — the array of `[text, language, note]`. Add or remove a form here.
- `SPOTS` — `[x%, y%, size, peak-opacity]`, one per name, hand-placed so the
  field reads as a constellation rather than a grid.
- `SCALE` — overall size of the names. `NARROW_FACTOR` thins them on phones.

`settle()` runs once the webfonts have loaded: it pushes overlapping names
apart and keeps every one inside the frame, and re-runs on resize. It
measures **relative to `#field`**, not the viewport, so it stays correct
after the page has been scrolled.

If you add to `NAMES` beyond the length of `SPOTS`, positions wrap around and
names will land on top of each other before `settle()` pulls them apart — add
a matching `SPOTS` entry too.

## Adding a link to the title page

Open `index.html`, find `<ul class="linklist">`, and copy one of the entries:

```html
<li>
  <a href="https://example.org" rel="noopener">The name of the thing</a>
  <p>One or two sentences on why it is worth someone's time.</p>
</li>
```

The two groups are `Ministry in Sydney` and `Resources`; add a new
`<h3 class="links-group">` if you want another. Do the same in
`index-cn.html` for the Chinese page. The little ↗ after each link is added
by the stylesheet — you do not type it.

---

## A standing decision about names

**The parish is named.** The title page links to St Paul's Anglican Church
Kogarah, and the introduction names it. That was decided on 19 August 2026,
after the one essay that criticised the congregation was withdrawn — see
`private/README.md`.

The rule that replaced anonymity is simpler and holds better: **write about
ideas and about yourself; do not publish an assessment of identifiable people
who did not consent to it.** Anonymising a parish never really worked, since
the site carries the author's name and the details converge. Not publishing
the criticism does.

So before publishing anything that describes the congregation, ask whether a
member reading it would recognise themselves in an unflattering paragraph. If
yes, it belongs in `private/`, or it needs rewriting as the general case.

## The mark

Two overlapping circles — two cultures — with the cross standing in the
overlap, its foot crossing the horizon.

## Changing the look

Everything visual lives in `style.css`, and the colours are the handful of
custom properties at the top. Change `--clay` and the whole site changes
with it.
