#!/usr/bin/env bash

set -eu

repo_uri="https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git"
remote_name="origin"
main_branch="master"
file_store_branch="file_store"


git config user.name "$GITHUB_ACTOR"
git config user.email "${GITHUB_ACTOR}@bots.github.com"


git checkout "$file_store_branch"

mkdir ./tmp/
cp -r ./contents ./tmp

git checkout "$main_branch"
mv ./tmp/contents/ .

python3 website_checker.py
cp -r ./contents/ ./tmp/

git checkout "$file_store_branch"
cp -r ./tmp/contents .
rm -rf ./tmp/

git add .

set +e  # Grep succeeds with nonzero exit codes to show results.

if git status | grep 'new file\|modified'
then
    set -e
    git commit -am "data updated on - $(date)"
    git remote set-url "$remote_name" "$repo_uri" # includes access token
    git push --force-with-lease "$remote_name" "$file_store_branch"
else
    set -e
    echo "No changes since last run"
fi

git checkout "$main_branch"

echo "finish"