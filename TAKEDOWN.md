# Taking the congregational culture essay off the live site

The essay was published before it was withdrawn, so it is currently readable
at `https://yungs.au/006-congregational-culture.html`. This removes it.

Two parts. **Part A takes it off the website** and takes five minutes. **Part
B removes it from the repository's history**, which is a separate problem and
is optional — read it and decide.

---

# Part A — take it off the site

## 1. Fix the folder on your Mac

In your local `cross-cultural-ministry` folder:

**Delete these two files:**

- `006-congregational-culture.html`
- `drafts/006-congregational-culture.md`

**Replace this one file** with the copy from the latest zip:

- `index.html`

> Do not simply copy the new zip over the top of the old folder. Copying
> adds and overwrites — it does **not** delete. The two files above have to
> be deleted by hand, or they will stay on the site.

Then move the `private/` folder from the latest zip into place if it is not
already there. It holds the essay, and it is in `.gitignore`, so it will
never be published.

## 2. Push the deletion

Open **GitHub Desktop**. You should see three changes:

| File | Shown as |
|---|---|
| `006-congregational-culture.html` | deleted (red minus) |
| `drafts/006-congregational-culture.md` | deleted (red minus) |
| `index.html` | modified |

If `private/` appears in that list, something is wrong with `.gitignore` —
stop and check before pushing.

1. Summary: `Withdraw the congregational culture essay`
2. **Commit to main**
3. **Push origin**

## 3. Check

Wait about a minute for the site to rebuild, then open:

`https://yungs.au/006-congregational-culture.html`

You want the site's own "Nothing here" page. If you still see the essay,
force a reload with **Command + Shift + R** — your browser has cached it.

Then check `https://yungs.au` lists five essays, 001 to 005.

---

# Part B — the repository history

Part A removes the essay from the website. It does **not** remove it from
the repository's history. Your repository is public, so the essay remains
readable at the commit that added it, at a URL like:

    https://github.com/w69gjcn72j-dotcom/cross-cultural-ministry/blob/<old-commit>/006-congregational-culture.html

Nobody stumbles on that by accident. But it is public, and "I deleted it" is
not the same as "it is gone".

## The clean fix: delete the repository and publish again

Because the whole history is one or two commits, throwing it away costs
almost nothing.

1. On GitHub, go to the repository → **Settings** → scroll to the bottom →
   **Delete this repository**. Type the name to confirm.
2. In **GitHub Desktop**, remove the local repository from the list
   (right-click → **Remove**, and choose to keep the files on disk).
3. In Finder, delete the hidden `.git` folder inside your
   `cross-cultural-ministry` folder.
   Press **Command + Shift + .** to see hidden files, delete `.git`, then
   press it again to re-hide.
4. Follow `GITHUB-DESKTOP.md` from the start. Same repository name, same
   settings.
5. Redo **Settings → Pages**: branch `main`, folder `/ (root)`.
   The custom domain should repopulate from the `CNAME` file. Re-tick
   **Enforce HTTPS** once the certificate is reissued.

Your DNS does not change and does not need touching.

The site is briefly unavailable between deleting and republishing — a few
minutes.

## Two smaller things

**Search engines.** The page was live for a short time, so it is unlikely to
have been indexed. If you want to check, search Google for
`site:yungs.au congregational`. If anything shows up, Google's Removals tool
(in Search Console) clears it faster than waiting.

**Anyone who already read it.** Nothing technical helps here. If it matters,
the pastoral answer is better than the technical one.

---

## What I would do

Part A today, without hesitation.

Part B if any of the people described would be hurt by finding it — which,
given the essay names contempt across cultures and a leader who hoarded keys
in a congregation of the size described, seems worth five minutes to me.
