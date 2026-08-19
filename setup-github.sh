#!/usr/bin/env bash
#
# setup-github.sh — put this site on GitHub Pages at yungs.au
#
# Run it once, from inside this folder:
#
#     cd /path/to/cross-cultural-ministry
#     bash setup-github.sh
#
# It is safe to run again: every step checks first and skips what is already
# done. It never touches any repository other than the one named below.
#
# What it does:
#   1. checks git and gh are present and you are logged in
#   2. makes this folder a git repository and commits everything
#   3. creates the public repo on GitHub (or reuses it if it exists)
#   4. pushes
#   5. turns on GitHub Pages from main / (root)
#   6. sets the custom domain to yungs.au
#   7. tells you exactly which DNS records to add, and checks them
#
# It does NOT touch DNS. That has to be done at Squarespace, by you.

set -euo pipefail

REPO="cross-cultural-ministry"
DOMAIN="yungs.au"
BRANCH="main"

# GitHub's apex addresses for Pages
A_RECORDS=(185.199.108.153 185.199.109.153 185.199.110.153 185.199.111.153)
AAAA_RECORDS=(2606:50c0:8000::153 2606:50c0:8001::153 2606:50c0:8002::153 2606:50c0:8003::153)

bold() { printf '\033[1m%s\033[0m\n' "$*"; }
ok()   { printf '  \033[32m✓\033[0m %s\n' "$*"; }
warn() { printf '  \033[33m!\033[0m %s\n' "$*"; }
die()  { printf '\033[31m✗ %s\033[0m\n' "$*" >&2; exit 1; }

# ---------------------------------------------------------------- 1. checks

bold "1. Checking the tools"

command -v git >/dev/null || die "git isn't installed. Install Xcode command line tools: xcode-select --install"
ok "git $(git --version | awk '{print $3}')"

if ! command -v gh >/dev/null; then
  cat <<'MSG'
  ✗ The GitHub CLI (gh) isn't installed.

    Either install it —      brew install gh && gh auth login
    or do it by hand — see PUSHING-BY-HAND.md in this folder.

MSG
  exit 1
fi
ok "gh $(gh --version | head -1 | awk '{print $3}')"

if ! gh auth status >/dev/null 2>&1; then
  die "gh isn't logged in. Run:  gh auth login"
fi

OWNER=$(gh api user --jq .login)
ok "logged in to GitHub as $OWNER"

[ -f index.html ] && [ -f add-post.py ] || die "Run this from inside the cross-cultural-ministry folder."

if command -v python3 >/dev/null; then
  python3 add-post.py --check || die "add-post.py --check failed. Fix that before publishing."
else
  warn "python3 not found, skipping add-post.py --check"
fi

# ------------------------------------------------------- 2. local repository

bold "2. Preparing the local repository"

if [ -d .git ]; then
  ok "already a git repository"
else
  git init -b "$BRANCH" >/dev/null
  ok "git repository created on branch $BRANCH"
fi

# make sure we're on the right branch name
CURRENT=$(git symbolic-ref --quiet --short HEAD || echo "")
if [ -n "$CURRENT" ] && [ "$CURRENT" != "$BRANCH" ]; then
  git branch -M "$BRANCH"
  ok "branch renamed to $BRANCH"
fi

cat > .gitignore <<'IGNORE'
.DS_Store
__pycache__/
*.pyc
~$*
IGNORE

git add -A
if git diff --cached --quiet 2>/dev/null; then
  ok "nothing new to commit"
else
  git commit -q -m "Cross-cultural ministry essays: site, converter and first six pieces"
  ok "committed $(git rev-list --count HEAD) revision(s)"
fi

# ---------------------------------------------------------- 3. remote repo

bold "3. The repository on GitHub"

if gh repo view "$OWNER/$REPO" >/dev/null 2>&1; then
  ok "$OWNER/$REPO already exists"
else
  gh repo create "$OWNER/$REPO" --public \
    --description "Essays on cross-cultural ministry — Rev David Yung" >/dev/null
  ok "created $OWNER/$REPO (public)"
fi

if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "https://github.com/$OWNER/$REPO.git"
else
  git remote add origin "https://github.com/$OWNER/$REPO.git"
fi
ok "origin points at https://github.com/$OWNER/$REPO.git"

# -------------------------------------------------------------- 4. push

bold "4. Pushing"

git push -u origin "$BRANCH"
ok "pushed to $BRANCH"

# -------------------------------------------------------------- 5. Pages

bold "5. Turning on GitHub Pages"

if gh api "repos/$OWNER/$REPO/pages" >/dev/null 2>&1; then
  ok "Pages is already on"
else
  gh api -X POST "repos/$OWNER/$REPO/pages" \
    -H "Accept: application/vnd.github+json" \
    --input - >/dev/null <<JSON
{"source": {"branch": "$BRANCH", "path": "/"}}
JSON
  ok "Pages enabled from $BRANCH / (root)"
fi

# -------------------------------------------------------- 6. custom domain

bold "6. Setting the custom domain"

CURRENT_CNAME=$(gh api "repos/$OWNER/$REPO/pages" --jq '.cname // ""' 2>/dev/null || echo "")
if [ "$CURRENT_CNAME" = "$DOMAIN" ]; then
  ok "custom domain is already $DOMAIN"
else
  gh api -X PUT "repos/$OWNER/$REPO/pages" \
    -H "Accept: application/vnd.github+json" \
    --input - >/dev/null <<JSON
{"cname": "$DOMAIN", "source": {"branch": "$BRANCH", "path": "/"}}
JSON
  ok "custom domain set to $DOMAIN"
fi

# --------------------------------------------------------------- 7. DNS

bold "7. DNS"

cat <<MSG

  This script does not touch DNS. Do this part at Squarespace.

  ORDER MATTERS. $DOMAIN points at Squarespace because of a preset block
  of records called "Squarespace Defaults". Squarespace's own guidance is
  blunt about it: your domain can't point to another site while those
  defaults are in place. So delete them first, then add GitHub's.

    1. Open your Squarespace domains dashboard
    2. Click $DOMAIN
    3. Click DNS, then DNS settings
    4. Find the SQUARESPACE DEFAULTS section and delete it with the red
       trash can. Confirm. (This does not affect your registration —
       you still own the domain.)
    5. Scroll to CUSTOM RECORDS and click Add Record for each row below
    6. Also delete any MX or other record you are not deliberately
       keeping for email, and remove any domain forwarding on @

  You will be asked for your password (or 2FA) before records can change.

  Records:

    Type    Host    Value
    ----    ----    -----
    A       @       ${A_RECORDS[0]}
    A       @       ${A_RECORDS[1]}
    A       @       ${A_RECORDS[2]}
    A       @       ${A_RECORDS[3]}
    AAAA    @       ${AAAA_RECORDS[0]}
    AAAA    @       ${AAAA_RECORDS[1]}
    AAAA    @       ${AAAA_RECORDS[2]}
    AAAA    @       ${AAAA_RECORDS[3]}
    CNAME   www     $OWNER.github.io

  The four AAAA records are IPv6. They are optional — the site works
  without them — but GitHub publishes them and they cost nothing to add.

  Delete any other A or CNAME record on @ or www, and remove any domain
  forwarding rule on @ — a leftover forward is the usual reason GitHub
  keeps saying "DNS check unsuccessful" long after the records look right.

MSG

if command -v dig >/dev/null; then
  FOUND=$(dig +short "$DOMAIN" A | sort | tr '\n' ' ')
  WANT=$(printf '%s\n' "${A_RECORDS[@]}" | sort | tr '\n' ' ')
  if [ "$FOUND" = "$WANT" ]; then
    ok "the four A records are live"
  elif [ -z "$FOUND" ]; then
    warn "no A records visible yet for $DOMAIN — add them at Squarespace"
  else
    warn "A records currently point at: $FOUND"
    warn "they should be: $WANT"
  fi

  WWW=$(dig +short "www.$DOMAIN" CNAME | sed 's/\.$//')
  if [ "$WWW" = "$OWNER.github.io" ]; then
    ok "www CNAME is live"
  elif [ -z "$WWW" ]; then
    warn "no www CNAME visible yet"
  else
    warn "www currently points at: $WWW (should be $OWNER.github.io)"
  fi
else
  warn "dig not available, skipping the DNS check"
fi

# --------------------------------------------------------------- 8. HTTPS

bold "8. HTTPS"

if gh api -X PUT "repos/$OWNER/$REPO/pages" \
     --input - >/dev/null 2>&1 <<JSON
{"https_enforced": true}
JSON
then
  ok "Enforce HTTPS is on"
else
  warn "HTTPS can't be enforced yet — GitHub has to issue the certificate first."
  warn "That happens once DNS resolves, and usually takes 15 minutes to an hour."
  warn "Re-run this script then, or tick the box yourself at:"
  warn "  https://github.com/$OWNER/$REPO/settings/pages"
fi

# ---------------------------------------------------------------- done

echo
bold "Done."
cat <<MSG

  Repository   https://github.com/$OWNER/$REPO
  Pages status https://github.com/$OWNER/$REPO/settings/pages
  Live at      https://$DOMAIN   (once DNS has propagated)

  Your study libraries have not been touched.

  From now on, publishing an essay is:

    python3 add-post.py my-essay.docx
    python3 add-post.py --check
    git add -A && git commit -m "Title" && git push

MSG
