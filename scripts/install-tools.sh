#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
tools_dir="$PWD/.tools"
mkdir -p "$tools_dir/hugo"
hugo_version="$(tr -d '\r\n' < .hugo-version)"
sass_version="$(tr -d '\r\n' < .sass-version)"
verify_archive() {
  local component="$1" version="$2" platform="$3" archive="$4"
  python3 - "$component" "$version" "$platform" "$archive" <<'PY'
import hashlib, json, pathlib, sys
component, version, platform, archive = sys.argv[1:]
expected = json.loads(pathlib.Path('scripts/tool-checksums.json').read_text())[component][version][platform]
actual = hashlib.sha256(pathlib.Path(archive).read_bytes()).hexdigest()
if actual != expected:
    raise SystemExit(f'Checksum mismatch: {component}')
PY
}
curl --fail --location --retry 3 --output "$tools_dir/hugo.tar.gz" "https://github.com/gohugoio/hugo/releases/download/v${hugo_version}/hugo_extended_${hugo_version}_linux-amd64.tar.gz"
verify_archive hugo "$hugo_version" linux-amd64 "$tools_dir/hugo.tar.gz"
tar -xf "$tools_dir/hugo.tar.gz" -C "$tools_dir/hugo"
curl --fail --location --retry 3 --output "$tools_dir/sass.tar.gz" "https://github.com/sass/dart-sass/releases/download/${sass_version}/dart-sass-${sass_version}-linux-x64.tar.gz"
verify_archive sass "$sass_version" linux-x64 "$tools_dir/sass.tar.gz"
tar -xf "$tools_dir/sass.tar.gz" -C "$tools_dir"
"$tools_dir/hugo/hugo" version
"$tools_dir/dart-sass/sass" --version
