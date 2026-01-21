#!/bin/bash
#
# Deploy to GitHub Pages with clean history
# Usage: ./scripts/deploy.sh [message]
#

set -e

msg="${1:-deploy}"

git add -A
git reset $(git commit-tree $(git write-tree) -m "$msg")
git push -f origin main

echo "Deployed"
