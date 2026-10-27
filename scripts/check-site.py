"""Check the built site's local references and migration-critical behavior."""

import csv
from html.parser import HTMLParser
import io
import json
import os
from pathlib import Path
import subprocess
import sys
from urllib.parse import unquote, urljoin, urlparse

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path(sys.argv[1] if len(sys.argv) > 1 else "public").resolve()
HOST = "fabiolopes.page"


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links, self.ids, self.hreflang, self.meta = [], set(), [], {}
        self.h1 = 0
        self.feed(text)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "h1":
            self.h1 += 1
        if tag == "meta":
            self.meta[attrs.get("name", attrs.get("property"))] = attrs.get("content")
        if tag == "link" and attrs.get("hreflang"):
            self.hreflang.append(attrs["hreflang"])
        if tag in ("a", "link", "script", "img"):
            target = attrs.get("href") if tag in ("a", "link") else attrs.get("src")
            if target:
                self.links.append((tag, target))


def output_path(url):
    target = OUTPUT / unquote(urlparse(url).path).lstrip("/")
    return target / "index.html" if target.is_dir() else target


def main():
    if not (OUTPUT / "index.html").exists():
        raise SystemExit(f"Build the site first: {OUTPUT}")
    errors = []
    pages = {path.resolve(): Page(path.read_text(encoding="utf-8")) for path in OUTPUT.rglob("*.html")}
    for path, page in pages.items():
        relative = path.relative_to(OUTPUT).as_posix()
        origin = f"https://{HOST}/" + relative.removesuffix("index.html")
        for tag, href in page.links:
            url = urlparse(urljoin(origin, href))
            if url.netloc != HOST or url.scheme not in ("http", "https"):
                continue
            target = output_path(url.geturl())
            if not target.exists():
                errors.append(f"Missing local resource: {relative}: {href}")
            elif tag == "a" and url.fragment and target.resolve() in pages:
                if unquote(url.fragment) not in pages[target.resolve()].ids:
                    errors.append(f"Missing anchor: {relative}: {href}")
    for relative in ("index.html", "pt-br/index.html", "projects/index.html", "pt-br/projetos/index.html", "about/index.html", "search/index.html", "pt-br/pesquisar/index.html", "archives/index.html", "pt-br/arquivo/index.html"):
        page = pages.get((OUTPUT / relative).resolve())
        if page is None or page.h1 != 1:
            errors.append(f"Expected one primary heading: {relative}")
        if page is None or not page.hreflang:
            errors.append(f"Missing translation metadata: {relative}")
        if page is not None and not page.meta.get("description"):
            errors.append(f"Missing description: {relative}")
    for relative in ("search/index.json", "pt-br/pesquisar/index.json", "sitemap.xml", "robots.txt"):
        if not (OUTPUT / relative).exists():
            errors.append(f"Missing site output: {relative}")
    for relative in ("index.html", "pt-br/index.html"):
        text = (OUTPUT / relative).read_text(encoding="utf-8")
        if "fonts.googleapis.com" in text:
            errors.append(f"Unexpected external font: {relative}")
        if "engineering-board" not in text or "work-card-03" not in text:
            errors.append(f"Missing portfolio content: {relative}")

    hugo = os.environ.get("HUGO_BIN", "hugo")
    listing = subprocess.run([hugo, "list", "all"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True)
    current = {row["path"]: row for row in csv.DictReader(io.StringIO(listing.stdout))}
    baseline = json.loads((ROOT / "docs/inventario-posts-2026-10-26.json").read_text(encoding="utf-8"))["posts"]
    for post in baseline:
        row = current.get(post["source"])
        if row is None or row["permalink"] != post["permalink"]:
            errors.append(f"Changed baseline article route: {post['source']}")
        if row is not None and row["date"] != post["date"]:
            errors.append(f"Changed original publication date: {post['source']}")
        if post["draft"] and output_path(post["permalink"]).exists():
            errors.append(f"Draft included in production: {post['source']}")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Site checks passed: {len(pages)} HTML pages, {len(baseline)} preserved article routes, EN/PT navigation and outputs.")


if __name__ == "__main__":
    main()
