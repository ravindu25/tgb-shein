#!/bin/sh
# Fetch the latest Nations Trust Bank USD selling rate and publish it to the site.
set -e
cd "$(dirname "$0")"
git pull -q --rebase
python3 scripts/update_rate.py
if [ -n "$(git status --porcelain rate.json)" ]; then
  git add rate.json
  git commit -q -m "Update NTB USD rate"
  git push -q
  echo "Published. The site shows the new rate within about a minute."
else
  echo "Nothing to publish."
fi
