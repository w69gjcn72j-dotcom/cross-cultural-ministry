# Putting this on GitHub without the gh CLI

`setup-github.sh` does all of this for you if you have the GitHub CLI
installed (`brew install gh && gh auth login`). If you would rather not
install it, here is the same thing by hand. It takes about three minutes.

---

## 1. Create the repository

Go to <https://github.com/new> and set:

- **Repository name** — `cross-cultural-ministry`
- **Public** — it has to be public for GitHub Pages on a free account
- **Do not** tick "Add a README", ".gitignore" or "Choose a license".
  The folder already has everything; an initialising commit only causes
  a conflict on the first push.

Click **Create repository**.

## 2. Push this folder

In Terminal, from inside this folder:

```
cd /path/to/cross-cultural-ministry

git init -b main
git add -A
git commit -m "Cross-cultural ministry essays: site, converter and first six pieces"
git remote add origin https://github.com/w69gjcn72j-dotcom/cross-cultural-ministry.git
git push -u origin main
```

If it asks for a password, it wants a personal access token, not your
GitHub password — <https://github.com/settings/tokens>, "Generate new
token (classic)", tick `repo`, and paste that as the password.

## 3. Turn on Pages

**Settings → Pages** in the new repository.

- **Source**: Deploy from a branch
- **Branch**: `main`, folder `/ (root)`
- **Save**

Give it a minute. A green banner appears with the `github.io` address.
Check the site works there before touching the domain.

## 4. Set the custom domain

Still on **Settings → Pages**, under **Custom domain**, enter:

```
yungs.au
```

and **Save**. (The `CNAME` file in this repository says the same thing, so
this may already be filled in.)

GitHub will show "DNS check unsuccessful" until step 5 is done and has
propagated. That is expected, not a fault.

## 5. DNS at Squarespace

`yungs.au` currently resolves to Squarespace's own web servers. Pointing the
apex at GitHub replaces that, which is the intention.

**There is no "disconnect" button.** For a domain registered with
Squarespace, the connection to the Squarespace site *is* a preset block of
DNS records called **Squarespace Defaults**. Squarespace's own guidance says
plainly that your domain can't point to another site while those defaults
are in place. So you delete them, and that is the disconnection.

1. Open your **domains dashboard** — <https://account.squarespace.com/domains>
2. Click **yungs.au**
3. Click **DNS**, then **DNS settings**
4. Find the **Squarespace Defaults** section and click the **red trash can**
   to delete it. Confirm.
   This does not affect your registration. You still own the domain, it
   still renews, and your email records are separate.
5. Scroll to **Custom Records** and click **Add Record** for each row below

You will be asked for your password, or to reauthenticate with 2FA, before
any record can be changed. Squarespace quotes 24–48 hours for propagation;
in practice it is usually minutes.

Also remove any **domain forwarding** rule on `@`, and check whether any
**MX records** are being used for email you still want — those you keep.

Then add:

| Type | Host | Value |
|---|---|---|
| A | @ | `185.199.108.153` |
| A | @ | `185.199.109.153` |
| A | @ | `185.199.110.153` |
| A | @ | `185.199.111.153` |
| AAAA | @ | `2606:50c0:8000::153` |
| AAAA | @ | `2606:50c0:8001::153` |
| AAAA | @ | `2606:50c0:8002::153` |
| AAAA | @ | `2606:50c0:8003::153` |
| CNAME | www | `w69gjcn72j-dotcom.github.io` |

The four **A** records are the ones that matter — they are GitHub Pages'
IPv4 addresses, the same for every Pages site in the world. The four
**AAAA** records are the IPv6 equivalents: optional, but published by GitHub
and free to add.

The **CNAME** is the only line that is specific to you. `w69gjcn72j-dotcom`
is your GitHub username, so the value is your Pages host — not the
repository name, and with no `https://` and no trailing slash. Some DNS
forms want a trailing dot (`w69gjcn72j-dotcom.github.io.`); Squarespace does
not.

Propagation is usually minutes, occasionally a few hours.

To watch it from Terminal:

```
dig +short yungs.au A
dig +short www.yungs.au CNAME
```

## 6. Enforce HTTPS

Back on **Settings → Pages**. Once DNS resolves, GitHub issues a Let's
Encrypt certificate — usually within the hour. When **Enforce HTTPS**
stops being greyed out, tick it.

---

## Afterwards

Publishing an essay becomes:

```
python3 add-post.py my-essay.docx
python3 add-post.py --check
git add -A && git commit -m "Title of the essay" && git push
```

Live in about a minute.

## If something goes wrong

**"Repository not found" on push** — the repository name or your username
is wrong in the `git remote add` line. Check with `git remote -v`.

**"Updates were rejected"** — GitHub created an initial commit (you ticked
README or license at step 1). Either delete the repository and start again
without ticking those, or run `git pull --rebase origin main` and push again.

**Pages builds but the site is blank** — check that `index.html` is at the
root of the repository, not inside a nested folder. On GitHub the file list
should show `index.html`, not `cross-cultural-ministry/index.html`.

**"DNS check unsuccessful" that never clears** — three usual causes, in
order of likelihood: the **Squarespace Defaults** block is still present; a
forwarding rule is still set on `@`; or an old A record survived the edit.
All four GitHub A records must be present on `@` and nothing else.

**The domain is a third-party one, not registered with Squarespace** — then
there are no Squarespace Defaults to delete. Instead, go to the Squarespace
site's **Settings → Domains**, remove the domain from the site, and make the
DNS changes at whichever registrar actually holds it.

**The site loads but the fonts look wrong** — that is fine on first load
while Google Fonts is still fetching. If it persists, the network is
blocking `fonts.googleapis.com`; the fallbacks (Georgia and the system
sans) are deliberate and readable.
