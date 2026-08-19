# Publishing with GitHub Desktop

Yes — if you have GitHub Desktop, use it. It is the best of the three
routes: no Terminal, and unlike the browser upload it sets you up properly,
so every future essay is two clicks rather than another drag-and-drop.

About five minutes.

---

## 1. Put the folder where you want it to live

Unzip `cross-cultural-ministry` somewhere sensible and permanent —
alongside your other site folders is ideal. GitHub Desktop will keep
pointing at wherever you leave it, so it is worth moving now rather than
later.

## 2. Add it to GitHub Desktop

1. **File → Add Local Repository…**
2. Choose the `cross-cultural-ministry` folder
3. Desktop will say the folder is not a Git repository, and offer a link to
   **create a repository** here. Click it.
4. The **Create a New Repository** dialog opens, with the name and path
   already filled in. Check:
   - **Name**: `cross-cultural-ministry`
   - **Initialize this repository with a README** — leave **unticked**
     (there is already a README in the folder)
   - **Git ignore**: **None** — there is already a `.gitignore` here
   - **License**: **None**
5. Click **Create repository**

Desktop now shows every file in the folder as a change waiting to be
committed. That is expected — it is the first commit, so everything is new.

## 3. Commit

Bottom left, there is a **Summary** box.

1. Type: `The site and the first six essays`
2. Click **Commit to main**

## 4. Publish

1. Click **Publish repository** in the bar along the top
2. **Name**: `cross-cultural-ministry`
3. **UNTICK "Keep this code private"**

   > This one matters. GitHub Pages does not serve private repositories on
   > a free account. If you leave it ticked, everything will appear to work
   > and the site will never come up.

4. Click **Publish repository**

Your files are now on GitHub.

## 5. Turn on Pages

This part is in the browser — Desktop does not do Pages settings.

1. Go to
   `https://github.com/w69gjcn72j-dotcom/cross-cultural-ministry/settings/pages`
2. **Source**: Deploy from a branch
3. **Branch**: `main`, folder **/ (root)** → **Save**

Wait a minute or two, then reload. A green box says the site is live.

## 6. Custom domain and HTTPS

Same page. **Custom domain** should already read `yungs.au`, because the
`CNAME` file was part of what you just published. If it is empty, type it
in and **Save**.

Your DNS is already correct, so the check passes within a few minutes.

**Enforce HTTPS** stays greyed out until GitHub issues a certificate for the
domain — normally fifteen minutes to an hour. Come back and tick it. That is
the final step.

---

## Then: https://yungs.au

---

## Publishing an essay from now on

This is the payoff. Once the above is done, every new piece is:

1. Write it in Word. First line is the title.
2. In Terminal *or* by double-clicking, run the converter:
   `python3 add-post.py my-essay.docx`
   (If you would rather not, send it to me and I will run it and hand back
   the finished files.)
3. Open **GitHub Desktop**. The new and changed files are listed.
4. Type a summary — the essay title will do.
5. **Commit to main**, then **Push origin**.

Live in about a minute. No Terminal needed for steps 3 to 5, ever.

## A note on what Desktop shows you

After a conversion you will typically see two or three changed files:

- `00N-your-slug.html` — the new essay, marked as added
- `index.html` — modified, because the browse list gained an entry
- occasionally `index-cn.html`, if it was a Chinese piece

If you see far more than that, something unexpected happened — stop and ask
before pushing. If you see fewer, the converter did not run.

## If something goes wrong

**"Publish repository" is greyed out** — you have not committed yet. Do
step 3 first.

**The repository published, but the site never appears** — nine times out of
ten this is the private/public checkbox. Go to the repository's
**Settings → General**, scroll to the bottom, **Change repository
visibility**, and make it public.

**Desktop lists thousands of files** — you have added a parent folder rather
than the `cross-cultural-ministry` folder itself. Remove the repository from
Desktop (right-click it in the list → **Remove**) and add the right folder.

**"Repository already exists on GitHub"** — you created it in the browser
earlier. Either delete it there and publish again, or use
**Repository → Repository settings… → Remote** to point at the existing one.
