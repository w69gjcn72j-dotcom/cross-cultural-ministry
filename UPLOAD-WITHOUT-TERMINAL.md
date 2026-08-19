# Putting the site up without using Terminal

This is the shortest route. No command line, no installing anything.
It is all drag-and-drop in a browser, and takes about five minutes.

There are 43 files here, the largest 37 KB. GitHub's browser uploader takes
up to 100 files at a time and 25 MB per file, so the whole site goes up in
one drag.

---

## Before you start: show hidden files

One file here is called `.nojekyll`. The dot at the front means macOS hides
it, and you need it in the upload.

In Finder, press **Command + Shift + . (full stop)**. Hidden files appear,
greyed out. Press the same keys again later to hide them.

---

## 1. Create the repository

1. Go to <https://github.com/new>
2. **Repository name**: `cross-cultural-ministry`
3. Choose **Public**
4. Leave "Add a README file", ".gitignore" and "license" **unticked**
5. Click **Create repository**

You land on a mostly empty page with some instructions on it. Ignore those.

## 2. Upload the files

1. On that page, find the link **uploading an existing file**
   (it is in the line "…or push an existing repository from the command
   line"). If you cannot see it, go straight to:
   `https://github.com/w69gjcn72j-dotcom/cross-cultural-ministry/upload/main`

2. In Finder, **open** the `cross-cultural-ministry` folder so you are
   looking at its contents — `index.html`, `style.css`, `icons`, and so on.

   > **Open the folder. Do not drag the folder itself.** If you drag the
   > folder, everything ends up one level down and the site will not work.

3. Press **Command + A** to select everything inside, then drag it all onto
   the browser window.

4. Wait for the list to finish appearing. You should see about 43 entries,
   including `index.html`, `CNAME` and `.nojekyll`.

5. In the **Commit changes** box at the bottom, type something like
   `The site and the first six essays`, then click **Commit changes**.

## 3. Turn on Pages

1. In the repository, click **Settings** (top right, with a cog)
2. In the left sidebar, click **Pages**
3. Under **Build and deployment** → **Source**, choose
   **Deploy from a branch**
4. Under **Branch**, choose **main** and folder **/ (root)**, then **Save**

Wait a minute or two. A box appears at the top saying the site is live.

## 4. Check the custom domain

Still on **Settings → Pages**, look at **Custom domain**.

Because the `CNAME` file was in the upload, it should already say
`yungs.au`. If it is empty, type `yungs.au` and click **Save**.

Your DNS records are already correct, so the check should pass within a few
minutes.

## 5. Enforce HTTPS

Same page, below the custom domain. **Enforce HTTPS** will be greyed out at
first while GitHub gets a security certificate for the domain — usually
fifteen minutes to an hour.

Come back later and tick it. That is the last step.

---

## Then visit https://yungs.au

If you see the six essays with the teal background, everything is done.

---

## Adding an essay later

Two ways.

**The easy way, in the browser.** In the repository, click **Add file** →
**Upload files**, drag the new `00N-something.html`, and commit. Then click
`index.html`, click the pencil icon, and add the new entry to the
`const POSTS = [` list, copying the shape of the ones already there.
Fiddly, but no software required.

**The better way, once you want it.** Install **GitHub Desktop** —
<https://desktop.github.com> — which is a normal Mac application with
buttons, not a command line. You "clone" the repository once, and after
that publishing is: run `add-post.py` on your Word document, open GitHub
Desktop, type a sentence, click **Commit**, click **Push**. That is the
workflow the rest of the documentation assumes.

You do not need it today.

---

## If something looks wrong

**The site loads but has no styling — plain black text on white.**
`style.css` did not make it into the upload, or the files went up inside a
folder. In the repository's file list you should see `index.html` at the
top level. If instead you see a single folder called
`cross-cultural-ministry`, that is the problem: click into it, and
re-upload the contents rather than the folder.

**"There isn't a GitHub Pages site here" at yungs.au.**
Either Pages is not switched on yet (step 3), or the first build has not
finished. Check **Settings → Pages** for the green "Your site is live" box.

**The custom domain box shows a red DNS error.**
Give it ten minutes and click **Check again**. Your records are correct — I
verified them — so this resolves itself.

**You cannot find `.nojekyll` in the upload list.**
It is optional for this site; nothing here needs it. Carry on without it.
