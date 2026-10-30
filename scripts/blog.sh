#!/usr/bin/env bash
set -euo pipefail

action="${1:-serve}"
if (( $# > 1 )) || [[ "$action" != serve && "$action" != build && "$action" != check ]]; then
  echo "Usage: $0 [serve|build|check]" >&2
  exit 2
fi

cd "$(dirname "${BASH_SOURCE[0]}")/.."
tools_dir="$PWD/.tools"
hugo="$tools_dir/hugo/hugo"
if [[ ! -x "$hugo" ]]; then
  echo 'Run bash scripts/install-tools.sh first.' >&2
  exit 1
fi

export PATH="$tools_dir/go/bin:$tools_dir/dart-sass:$PATH"
export GOENV=off
export GOMODCACHE="$tools_dir/gomod"
export GOCACHE="$tools_dir/gocache"
export HUGO_CACHEDIR="$tools_dir/hugocache"
export PYTHONDONTWRITEBYTECODE=1
export HUGO_BIN="$hugo"

if [[ "$action" == serve ]]; then
  exec "$hugo" server --environment development --buildDrafts --disableFastRender --destination "$tools_dir/preview"
fi

if [[ "$action" == check ]]; then
  python3 -m unittest discover -s tests -v
fi
"$hugo" --environment production --gc --minify --cleanDestinationDir --printPathWarnings --panicOnWarning
if [[ "$action" == check ]]; then
  python3 scripts/check-site.py public
fi
