# Adding an essay — without ever opening Terminal

`tools/convert.html` does what `add-post.py` does, but in your browser.
Double-click it. Nothing to install, no command line, and it works offline —
the file never leaves your Mac.

---

## The whole routine

1. **Write the essay in Word.** The first line is the title. Save it as
   `.docx` anywhere you like.

2. **Double-click `tools/convert.html`.** It opens in your browser.

3. **Drag the Word file onto the first box.**

4. **Drag `essays.html` onto the second box** — it is in the project folder.
   This is how the converter knows which number the new essay should get and
   hands you back the updated list.

5. **Check the details.** Title, summary, web address, date and number are
   filled in for you. Change any of them; the preview updates as you type.
   Anything you edit by hand is left alone from then on.

6. **Look at the preview.** This is the actual converted text. If a heading
   has not come out as a heading, fix it in Word and drag the file in again.

7. **Click both download buttons.** You get `00N-your-slug.html` and a fresh
   `essays.html`.

8. **Move both into the project folder**, replacing the old `essays.html`
   when Finder asks.

9. **Open GitHub Desktop.** One new file, one modified file. Type the essay
   title, **Commit to main**, **Push origin**.

Live in about a minute.

---

## What the converter understands

Exactly what `add-post.py` understands, so the two produce the same pages:

| In Word | You get |
|---|---|
| first line | the title |
| `Summary: …` or `摘要：…` | the box under the title, and the browse-page line |
| Word's **Heading 1 / 2** | a section heading |
| Word's **Heading 3 / 4** | a smaller heading |
| `## A heading` typed by hand | the same |
| `> A quotation` | a pulled quotation |
| `- a point` / Word's bullet lists | a bullet |
| `1. a point` / Word's numbered lists | a numbered list |
| `---` on its own line | a dividing rule |
| **bold** and *italic*, typed or from Word | emphasis |
| Word tables | a table |

Chinese is detected automatically and the file is named with `-cn`. Drag
`essays-cn.html` in at step 4 rather than `essays.html`.

If a title already in the list comes through again, the converter says so and
**updates that essay in place** rather than adding a second copy — which is
how you publish a revision.

---

## Things it will not do

**Figures, videos and reference lists.** The `[figure: …]`, `[youtube: …]`
and `[sources]` markers only work in `add-post.py`. If an essay needs one,
send it to me and I will build that page for you.

**Check the whole site.** `add-post.py --check` verifies every entry has a
page and vice versa. The converter cannot, because it only ever sees two
files. In practice GitHub Desktop is the safety net: if you see anything
other than one added file and one modified file, stop before pushing.

---

## If something goes wrong

**"This browser can't unzip files on its own."** Very old browser. Chrome,
Edge, or Safari 16.4 and later all work.

**"That doesn't look like a .docx file."** It is probably an old `.doc`. Open
it in Word and **Save As** → Word Document (.docx).

**"Couldn't find the POSTS list in that file."** You dragged in the wrong
HTML file at step 4. It should be `essays.html` — the browse page — not
`index.html` and not an essay.

**The preview looks like one long wall of text.** The headings in your Word
document are not styled as headings. Either apply Word's Heading 1 style, or
type `## ` in front of each heading line.

**A downloaded file is called `essays (1).html`.** Your browser would not
overwrite the earlier download. Rename it to `essays.html` when you move it
into the folder.

---

## The command-line way, if you ever want it

Still there, unchanged, and it does a little more:

```
python3 add-post.py my-essay.docx
python3 add-post.py --check
```

You do not need it. It is documented in `README.md` for the day you might.
