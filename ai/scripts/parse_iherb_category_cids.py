"""Parse iHerb category links into a category-name to cids mapping."""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.parse import parse_qs, urljoin, urlparse
from urllib.request import Request, urlopen


DEFAULT_URL = "https://kr.iherb.com/c/supplements"
DEFAULT_LINK_TEMPLATE = "https://kr.iherb.com/c/supplements?cids={cid}"
DEFAULT_JSON_OUTPUT = Path("ai_data/iherb_category_cids.json")
DEFAULT_CSV_OUTPUT = Path("ai_data/iherb_category_cids.csv")
DEFAULT_TREE_OUTPUT = Path("ai_data/iherb_category_tree.json")
DEFAULT_FLAT_JSON_OUTPUT = Path("ai_data/iherb_category_flat.json")
DEFAULT_FLAT_CSV_OUTPUT = Path("ai_data/iherb_category_flat.csv")
DEFAULT_META_OUTPUT = Path("ai_data/iherb_category_crawl_meta.json")
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0 Safari/537.36"
)


@dataclass(frozen=True)
class CategoryLink:
    name: str
    cid: str | None
    url: str
    parent_id: str | None = None


@dataclass
class CategoryNode:
    name: str
    cid: str
    url: str
    parent_id: str | None
    children: list["CategoryNode"]


class IherbCategoryLinkParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.links: list[CategoryLink] = []
        self._active_href: str | None = None
        self._active_label: str | None = None
        self._text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return

        attr_map = {key.lower(): value for key, value in attrs if value}
        href = attr_map.get("href")
        if not href or not is_category_href(href):
            return

        self._active_href = href
        self._active_label = attr_map.get("aria-label") or attr_map.get("title")
        self._text_parts = []

    def handle_data(self, data: str) -> None:
        if self._active_href:
            self._text_parts.append(data)

    def handle_entityref(self, name: str) -> None:
        if self._active_href:
            self._text_parts.append(html.unescape(f"&{name};"))

    def handle_charref(self, name: str) -> None:
        if self._active_href:
            self._text_parts.append(html.unescape(f"&#{name};"))

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "a" or not self._active_href:
            return

        href = self._active_href
        name = clean_name(" ".join(self._text_parts)) or clean_name(self._active_label or "")
        cid = extract_cid(href)
        if name:
            self.links.append(CategoryLink(name=name, cid=cid, url=urljoin(self.base_url, href)))

        self._active_href = None
        self._active_label = None
        self._text_parts = []


class IherbHierarchyCategoryParser(HTMLParser):
    def __init__(self, link_template: str) -> None:
        super().__init__(convert_charrefs=True)
        self.link_template = link_template
        self.links: list[CategoryLink] = []
        self._active_attrs: dict[str, str] | None = None
        self._text_parts: list[str] = []
        self._inside_name_span = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {key.lower(): value for key, value in attrs if value}
        class_names = set((attr_map.get("class") or "").split())

        if tag.lower() in {"a", "button"} and "hierarchy-category-filter-link" in class_names:
            cid = attr_map.get("data-category-id") or attr_map.get("data-ga-event-label")
            if not cid:
                return
            self._active_attrs = attr_map
            self._text_parts = []
            return

        if self._active_attrs and tag.lower() == "span" and "hierarchy-category-filter-name" in class_names:
            self._inside_name_span = True

    def handle_data(self, data: str) -> None:
        if self._active_attrs and self._inside_name_span:
            self._text_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "span":
            self._inside_name_span = False
            return

        if tag not in {"a", "button"} or not self._active_attrs:
            return

        cid = self._active_attrs.get("data-category-id") or self._active_attrs.get("data-ga-event-label")
        name = clean_name(" ".join(self._text_parts)) or clean_name(self._active_attrs.get("title") or "")
        parent_id = self._active_attrs.get("data-parent-id")
        if cid and name:
            self.links.append(
                CategoryLink(
                    name=name,
                    cid=cid,
                    url=self.link_template.format(cid=cid),
                    parent_id=parent_id,
                )
            )
        self._active_attrs = None
        self._text_parts = []
        self._inside_name_span = False


def extract_cid(url: str) -> str | None:
    query = parse_qs(urlparse(url).query)
    cid_values = query.get("cids")
    if cid_values and cid_values[0].strip():
        return cid_values[0].strip()

    match = re.search(r"[?&]cids=([^&#]+)", url)
    return match.group(1).strip() if match else None


def is_category_href(url: str) -> bool:
    if extract_cid(url):
        return True

    parsed = urlparse(url)
    return parsed.path.startswith("/c/") or "/c/" in parsed.path


def clean_name(value: str) -> str:
    value = html.unescape(value)
    value = re.sub(r"\s+", " ", value).strip()
    value = re.sub(r"\s*\(\d+\)\s*$", "", value).strip()
    return value


def fetch_html(url: str, timeout: float) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Referer": "https://kr.iherb.com/",
            "Upgrade-Insecure-Requests": "1",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def parse_category_links(page_html: str, base_url: str) -> list[CategoryLink]:
    parser = IherbCategoryLinkParser(base_url=base_url)
    parser.feed(page_html)
    return deduplicate_links(parser.links)


def parse_hierarchy_categories(page_html: str, link_template: str) -> list[CategoryLink]:
    parser = IherbHierarchyCategoryParser(link_template=link_template)
    parser.feed(page_html)
    return deduplicate_links_preserving_order(parser.links)


def deduplicate_links_preserving_order(links: Iterable[CategoryLink]) -> list[CategoryLink]:
    seen: set[str] = set()
    deduped: list[CategoryLink] = []
    for link in links:
        key = link.cid or link.url
        if key in seen:
            continue
        seen.add(key)
        deduped.append(link)
    return deduped


def extract_page_category(page_html: str, url: str) -> CategoryLink | None:
    cid_match = re.search(r"\bCATEGORY_ID\s*=\s*[\"']([^\"']+)[\"']", page_html)
    if not cid_match:
        return None

    cid = cid_match.group(1).strip()
    if not cid or cid == "0":
        return None

    name = ""
    name_match = re.search(r"\bCATEGORY_NAME\s*=\s*[\"']([^\"']+)[\"']", page_html)
    if name_match:
        raw_name = name_match.group(1)
        name = clean_name(raw_name.encode("utf-8").decode("unicode_escape") if "\\u" in raw_name else raw_name)

    if not name:
        title_match = re.search(r"<title[^>]*>(.*?)</title>", page_html, flags=re.IGNORECASE | re.DOTALL)
        if title_match:
            name = clean_name(re.sub(r"\|.*$", "", title_match.group(1)))

    return CategoryLink(name=name, cid=cid, url=url) if name else None


def resolve_missing_cids(
    links: Iterable[CategoryLink],
    timeout: float,
    max_pages: int,
) -> list[CategoryLink]:
    resolved: list[CategoryLink] = []
    pages_fetched = 0
    seen_urls: set[str] = set()

    for link in links:
        if link.cid:
            resolved.append(link)
            continue
        if pages_fetched >= max_pages or link.url in seen_urls:
            continue

        seen_urls.add(link.url)
        pages_fetched += 1
        try:
            page_category = extract_page_category(fetch_html(link.url, timeout), link.url)
        except Exception as error:
            print(f"Skipping {link.url}: {error}", file=sys.stderr)
            continue
        if page_category:
            resolved.append(page_category)

    return deduplicate_links(resolved)


def crawl_hierarchy(
    start_url: str,
    link_template: str,
    timeout: float,
    max_pages: int,
    max_depth: int,
    progress_every: int,
    skip_duplicate_cids: bool,
) -> tuple[CategoryNode, dict[str, object]]:
    pages_fetched = 0
    hit_max_pages = False
    child_cache: dict[str, list[CategoryLink]] = {}
    category_cache: dict[str, CategoryLink] = {}
    emitted_cids: set[str] = set()

    def fetch_category_page(url: str) -> tuple[CategoryLink, list[CategoryLink]]:
        nonlocal pages_fetched

        page_html = fetch_html(url, timeout)
        pages_fetched += 1
        if progress_every > 0 and pages_fetched % progress_every == 0:
            print(f"Fetched {pages_fetched} category pages...", file=sys.stderr)

        hierarchy = parse_hierarchy_categories(page_html, link_template)
        page_category = extract_page_category(page_html, url)
        current = first_current_category(hierarchy, url) or page_category
        if not current or not current.cid:
            raise ValueError(f"Could not identify category for {url}")

        children = [link for link in hierarchy if link.parent_id == current.cid and link.cid != current.cid]
        category_cache[current.cid] = CategoryLink(
            name=current.name,
            cid=current.cid,
            url=link_template.format(cid=current.cid),
            parent_id=current.parent_id,
        )
        child_cache[current.cid] = children
        return category_cache[current.cid], children

    def build_node(link: CategoryLink, depth: int, path: set[str]) -> CategoryNode:
        nonlocal hit_max_pages

        if not link.cid:
            raise ValueError(f"Missing cid for {link.name}")
        emitted_cids.add(link.cid)

        node = CategoryNode(
            name=link.name,
            cid=link.cid,
            url=link.url,
            parent_id=link.parent_id,
            children=[],
        )

        if depth >= max_depth or link.cid in path:
            return node

        if link.cid in child_cache:
            children = child_cache[link.cid]
        elif pages_fetched >= max_pages:
            hit_max_pages = True
            return node
        else:
            try:
                fetched_link, children = fetch_category_page(link.url)
            except Exception as error:
                print(f"Skipping {link.url}: {error}", file=sys.stderr)
                return node
            node.name = fetched_link.name
            node.url = fetched_link.url

        next_path = {*path, link.cid}
        node.children = []
        for child in children:
            if not child.cid or child.cid in path:
                continue
            if skip_duplicate_cids and child.cid in emitted_cids:
                continue
            node.children.append(build_node(child, depth + 1, next_path))
        return node

    root_link, _ = fetch_category_page(start_url)
    root = build_node(root_link, depth=0, path=set())
    print(f"Fetched {pages_fetched} category pages.", file=sys.stderr)
    return root, {
        "start_url": start_url,
        "pages_fetched": pages_fetched,
        "max_pages": max_pages,
        "max_depth": max_depth,
        "hit_max_pages": hit_max_pages,
        "skip_duplicate_cids": skip_duplicate_cids,
    }


def first_current_category(links: Iterable[CategoryLink], url: str) -> CategoryLink | None:
    for link in links:
        if link.parent_id is None and link.cid:
            return CategoryLink(name=link.name, cid=link.cid, url=url, parent_id=None)
    return None


def category_node_to_dict(node: CategoryNode) -> dict[str, object]:
    return {
        "name": node.name,
        "cids": node.cid,
        "url": node.url,
        "parent_id": node.parent_id,
        "children": [category_node_to_dict(child) for child in node.children],
    }


def flatten_category_tree(node: CategoryNode) -> list[dict[str, str | int | None]]:
    rows: list[dict[str, str | int | None]] = []

    def walk(current: CategoryNode, depth: int, path_names: list[str], path_cids: list[str]) -> None:
        current_path_names = [*path_names, current.name]
        current_path_cids = [*path_cids, current.cid]
        rows.append(
            {
                "depth": depth,
                "name": current.name,
                "cids": current.cid,
                "url": current.url,
                "parent_id": current.parent_id,
                "path": " > ".join(current_path_names),
                "path_cids": " > ".join(current_path_cids),
            }
        )
        for child in current.children:
            walk(child, depth + 1, current_path_names, current_path_cids)

    walk(node, depth=0, path_names=[], path_cids=[])
    return rows


def deduplicate_links(links: Iterable[CategoryLink]) -> list[CategoryLink]:
    by_cid: dict[str, CategoryLink] = {}
    for link in links:
        if not link.cid:
            continue
        current = by_cid.get(link.cid)
        if current is None or is_better_name(link.name, current.name):
            by_cid[link.cid] = link
    return sorted(by_cid.values(), key=lambda item: item.name.casefold())


def is_better_name(candidate: str, current: str) -> bool:
    if candidate == current:
        return False
    if current.isdigit():
        return True
    if candidate.isdigit():
        return False
    return len(candidate) < len(current)


def write_json(links: Iterable[CategoryLink], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    mapping: dict[str, str | list[str]] = {}
    for link in links:
        if not link.cid:
            continue
        current = mapping.get(link.name)
        if current is None:
            mapping[link.name] = link.cid
        elif isinstance(current, list):
            if link.cid not in current:
                current.append(link.cid)
        elif current != link.cid:
            mapping[link.name] = [current, link.cid]
    output_path.write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(links: Iterable[CategoryLink], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["name", "cids", "url"])
        writer.writeheader()
        for link in links:
            if link.cid:
                writer.writerow({"name": link.name, "cids": link.cid, "url": link.url})


def write_links_csv(links: Iterable[CategoryLink], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["name", "url", "cids", "parent_id"])
        writer.writeheader()
        for link in links:
            writer.writerow(
                {
                    "name": link.name,
                    "url": link.url,
                    "cids": link.cid or "",
                    "parent_id": link.parent_id or "",
                }
            )


def write_links_json(links: Iterable[CategoryLink], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            "name": link.name,
            "url": link.url,
            "cids": link.cid,
            "parent_id": link.parent_id,
        }
        for link in links
    ]
    output_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_tree_json(node: CategoryNode, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(category_node_to_dict(node), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_flat_json(rows: Iterable[dict[str, str | int | None]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(list(rows), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_flat_csv(rows: Iterable[dict[str, str | int | None]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["depth", "name", "cids", "url", "parent_id", "path", "path_cids"])
        writer.writeheader()
        writer.writerows(rows)


def write_meta_json(meta: dict[str, object], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL, help="iHerb category page URL to parse")
    parser.add_argument("--html-file", type=Path, help="Parse a saved HTML file instead of fetching URL")
    parser.add_argument(
        "--hierarchy-html-file",
        type=Path,
        help="Parse iHerb hierarchy category filter HTML with data-category-id buttons",
    )
    parser.add_argument(
        "--links-json",
        type=Path,
        help='Read category links from JSON, e.g. [{"name": "아답토젠", "url": "https://..."}]',
    )
    parser.add_argument(
        "--crawl-hierarchy",
        action="store_true",
        help="Recursively visit iHerb category URLs and build tree/flat category outputs",
    )
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_OUTPUT)
    parser.add_argument("--csv-output", type=Path, default=DEFAULT_CSV_OUTPUT)
    parser.add_argument("--tree-output", type=Path, default=DEFAULT_TREE_OUTPUT)
    parser.add_argument("--flat-json-output", type=Path, default=DEFAULT_FLAT_JSON_OUTPUT)
    parser.add_argument("--flat-csv-output", type=Path, default=DEFAULT_FLAT_CSV_OUTPUT)
    parser.add_argument("--meta-output", type=Path, default=DEFAULT_META_OUTPUT)
    parser.add_argument("--link-template", default=DEFAULT_LINK_TEMPLATE)
    parser.add_argument(
        "--follow-category-pages",
        action="store_true",
        help="Visit /c/... links and read CATEGORY_ID from each category page",
    )
    parser.add_argument("--max-pages", type=int, default=80, help="Maximum category pages to fetch")
    parser.add_argument("--max-depth", type=int, default=6, help="Maximum hierarchy depth to crawl")
    parser.add_argument("--progress-every", type=int, default=25, help="Print crawl progress every N fetched pages")
    parser.add_argument(
        "--keep-duplicate-cids",
        action="store_true",
        help="Keep duplicate cids when the same category appears under multiple paths",
    )
    parser.add_argument("--allow-empty", action="store_true", help="Write empty output files when nothing is parsed")
    parser.add_argument("--timeout", type=float, default=20.0)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    links: list[CategoryLink] = []

    if args.crawl_hierarchy:
        root, meta = crawl_hierarchy(
            start_url=args.url,
            link_template=args.link_template,
            timeout=args.timeout,
            max_pages=args.max_pages,
            max_depth=args.max_depth,
            progress_every=args.progress_every,
            skip_duplicate_cids=not args.keep_duplicate_cids,
        )
        flat_rows = flatten_category_tree(root)
        meta["flat_rows"] = len(flat_rows)
        meta["unique_cids"] = len({row["cids"] for row in flat_rows})
        meta["max_observed_depth"] = max((int(row["depth"]) for row in flat_rows), default=0)
        write_tree_json(root, args.tree_output)
        write_flat_json(flat_rows, args.flat_json_output)
        write_flat_csv(flat_rows, args.flat_csv_output)
        write_meta_json(meta, args.meta_output)
        print(f"Crawled {len(flat_rows)} iHerb category tree rows.")
        print(f"Tree JSON: {args.tree_output}")
        print(f"Flat JSON: {args.flat_json_output}")
        print(f"Flat CSV: {args.flat_csv_output}")
        print(f"Meta JSON: {args.meta_output}")
        return 0

    if args.hierarchy_html_file:
        page_html = args.hierarchy_html_file.read_text(encoding="utf-8")
        links = parse_hierarchy_categories(page_html, args.link_template)
        if not links and not args.allow_empty:
            print("Parsed 0 iHerb hierarchy categories; output files were not changed.", file=sys.stderr)
            return 1

        write_links_json(links, args.json_output)
        write_links_csv(links, args.csv_output)
        print(f"Parsed {len(links)} iHerb hierarchy categories.")
        print(f"JSON: {args.json_output}")
        print(f"CSV: {args.csv_output}")
        return 0

    if args.links_json:
        raw_links = json.loads(args.links_json.read_text(encoding="utf-8"))
        for item in raw_links:
            name = clean_name(item.get("name") or item.get("text") or "")
            url = item.get("url") or item.get("href")
            if name and url:
                links.append(CategoryLink(name=name, cid=extract_cid(url), url=url))
    else:
        page_html = args.html_file.read_text(encoding="utf-8") if args.html_file else fetch_html(args.url, args.timeout)
        links = parse_category_links(page_html, args.url)
        page_category = extract_page_category(page_html, args.url)
        if page_category:
            links.append(page_category)
    if args.follow_category_pages:
        links = resolve_missing_cids(links, args.timeout, args.max_pages)
    else:
        links = deduplicate_links(links)

    if not links and not args.allow_empty:
        print("Parsed 0 iHerb category cids; output files were not changed.", file=sys.stderr)
        return 1

    write_json(links, args.json_output)
    write_csv(links, args.csv_output)

    print(f"Parsed {len(links)} iHerb category cids.")
    print(f"JSON: {args.json_output}")
    print(f"CSV: {args.csv_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
