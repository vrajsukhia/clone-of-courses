#!/usr/bin/env python3
"""
Fetch assets from https://www.mygreatlearning.com/academy for private,
educational, non-commercial use. This script does not attempt to bypass
paywalls or logins.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import posixpath
import re
import sys
import time
import urllib.robotparser
from dataclasses import dataclass
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urldefrag, urljoin, urlparse
from urllib.request import Request, urlopen

ALLOWED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".svg",
    ".ico",
    ".gif",
    ".woff",
    ".woff2",
    ".ttf",
    ".otf",
}

MIME_EXTENSION_MAP = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/webp": ".webp",
    "image/svg+xml": ".svg",
    "image/x-icon": ".ico",
    "image/vnd.microsoft.icon": ".ico",
    "image/gif": ".gif",
    "font/woff": ".woff",
    "font/woff2": ".woff2",
    "font/ttf": ".ttf",
    "font/otf": ".otf",
    "application/font-woff": ".woff",
    "application/font-woff2": ".woff2",
}

RETRYABLE_STATUS = {429, 500, 502, 503, 504}

URL_RE = re.compile(r"url\(\s*(?P<quote>['\"]?)(?P<url>[^'\")\s]+)(?P=quote)\s*\)", re.IGNORECASE)
IMPORT_RE = re.compile(
    r"@import\s+(?:url\()?\s*(?P<quote>['\"]?)(?P<url>[^'\")\s;]+)(?P=quote)\s*\)?",
    re.IGNORECASE,
)


@dataclass
class FetchResult:
    ok: bool
    blocked: bool
    status: Optional[int] = None
    final_url: Optional[str] = None
    content_type: Optional[str] = None
    data: Optional[bytes] = None
    text: Optional[str] = None
    error: Optional[str] = None


@dataclass
class Summary:
    assets_found: int = 0
    assets_downloaded: int = 0
    assets_skipped_external: int = 0
    assets_skipped_robots: int = 0
    assets_failed: int = 0
    css_processed: int = 0
    css_skipped_external: int = 0
    css_skipped_robots: int = 0
    css_failed: int = 0


class RobotsCache:
    def __init__(self, fetcher: "Fetcher") -> None:
        self.fetcher = fetcher
        self.parsers: Dict[str, urllib.robotparser.RobotFileParser] = {}

    def can_fetch(self, user_agent: str, url: str) -> bool:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False
        key = f"{parsed.scheme}://{parsed.netloc}"
        if key not in self.parsers:
            robots_url = f"{key}/robots.txt"
            result = self.fetcher.fetch_text(robots_url, check_robots=False)
            parser = urllib.robotparser.RobotFileParser()
            if result.ok and result.text:
                parser.parse(result.text.splitlines())
            else:
                parser.parse([])
            self.parsers[key] = parser
        return self.parsers[key].can_fetch(user_agent, url)


class Fetcher:
    def __init__(self, user_agent: str, delay: float, timeout: float, retries: int) -> None:
        self.user_agent = user_agent
        self.delay = delay
        self.timeout = timeout
        self.retries = retries
        self.last_request_time: Dict[str, float] = {}
        self.robots = RobotsCache(self)

    def _respect_delay(self, netloc: str) -> None:
        now = time.time()
        last = self.last_request_time.get(netloc)
        if last is not None:
            elapsed = now - last
            if elapsed < self.delay:
                time.sleep(self.delay - elapsed)
        self.last_request_time[netloc] = time.time()

    def _request(self, url: str) -> FetchResult:
        parsed = urlparse(url)
        self._respect_delay(parsed.netloc)
        request = Request(url, headers={"User-Agent": self.user_agent})
        with urlopen(request, timeout=self.timeout) as response:
            data = response.read()
            content_type = response.headers.get("Content-Type")
            status = getattr(response, "status", None)
            return FetchResult(
                ok=True,
                blocked=False,
                status=status,
                final_url=response.geturl(),
                content_type=content_type,
                data=data,
            )

    def fetch_binary(self, url: str, check_robots: bool = True) -> FetchResult:
        if check_robots and not self.robots.can_fetch(self.user_agent, url):
            return FetchResult(ok=False, blocked=True)
        for attempt in range(1, self.retries + 1):
            try:
                return self._request(url)
            except HTTPError as exc:
                if exc.code in RETRYABLE_STATUS and attempt < self.retries:
                    time.sleep(0.5 * attempt)
                    continue
                return FetchResult(ok=False, blocked=False, status=exc.code, error=str(exc))
            except URLError as exc:
                if attempt < self.retries:
                    time.sleep(0.5 * attempt)
                    continue
                return FetchResult(ok=False, blocked=False, error=str(exc))
            except OSError as exc:
                if attempt < self.retries:
                    time.sleep(0.5 * attempt)
                    continue
                return FetchResult(ok=False, blocked=False, error=str(exc))
        return FetchResult(ok=False, blocked=False, error="Retries exhausted")

    def fetch_text(self, url: str, check_robots: bool = True) -> FetchResult:
        result = self.fetch_binary(url, check_robots=check_robots)
        if not result.ok:
            return result
        encoding = extract_charset(result.content_type)
        try:
            result.text = (result.data or b"").decode(encoding, errors="replace")
        except LookupError:
            result.text = (result.data or b"").decode("utf-8", errors="replace")
        return result


class AssetHtmlParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=False)
        self.base_url = base_url
        self.asset_urls: Set[str] = set()
        self.css_urls: Set[str] = set()
        self._in_style_tag = False
        self._style_buffer: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        attr_map = {name.lower(): value for name, value in attrs if value is not None}
        tag = tag.lower()
        if tag == "style":
            self._in_style_tag = True
            self._style_buffer = []
        if tag == "img":
            self._collect_asset(attr_map.get("src"))
            self._collect_srcset(attr_map.get("srcset"))
        elif tag == "source":
            self._collect_srcset(attr_map.get("srcset"))
            self._collect_asset(attr_map.get("src"))
        elif tag == "link":
            rel = (attr_map.get("rel") or "").lower()
            as_attr = (attr_map.get("as") or "").lower()
            href = attr_map.get("href")
            if "stylesheet" in rel or as_attr == "style":
                self._collect_css(href)
            if "icon" in rel or "apple-touch-icon" in rel or "mask-icon" in rel:
                self._collect_asset(href)
            if "preload" in rel and as_attr in {"image", "font"}:
                self._collect_asset(href)
        elif tag == "meta":
            prop = (attr_map.get("property") or attr_map.get("name") or "").lower()
            if prop in {"og:image", "twitter:image", "msapplication-tileimage"}:
                self._collect_asset(attr_map.get("content"))
        inline_style = attr_map.get("style")
        if inline_style:
            self._collect_css_text(inline_style)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "style":
            css_text = "".join(self._style_buffer)
            if css_text.strip():
                self._collect_css_text(css_text)
            self._style_buffer = []
            self._in_style_tag = False

    def handle_data(self, data: str) -> None:
        if self._in_style_tag:
            self._style_buffer.append(data)

    def _collect_asset(self, value: Optional[str]) -> None:
        url = normalize_url(resolve_url(self.base_url, value))
        if url:
            self.asset_urls.add(url)

    def _collect_css(self, value: Optional[str]) -> None:
        url = normalize_url(resolve_url(self.base_url, value))
        if url:
            self.css_urls.add(url)

    def _collect_srcset(self, value: Optional[str]) -> None:
        if not value:
            return
        for url in parse_srcset(value):
            abs_url = normalize_url(resolve_url(self.base_url, url))
            if abs_url:
                self.asset_urls.add(abs_url)

    def _collect_css_text(self, css_text: str) -> None:
        imports, assets = extract_css_links(css_text, self.base_url)
        for import_url in imports:
            self.css_urls.add(import_url)
        self.asset_urls.update(assets)


class HtmlRewriter(HTMLParser):
    def __init__(
        self,
        base_url: str,
        asset_map: Dict[str, str],
        css_map: Dict[str, str],
        html_rel_path: str,
    ) -> None:
        super().__init__(convert_charrefs=False)
        self.base_url = base_url
        self.asset_map = asset_map
        self.css_map = css_map
        self.html_rel_path = html_rel_path
        self.output: List[str] = []
        self._in_style_tag = False
        self._style_buffer: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        tag_lower = tag.lower()
        if tag_lower == "style":
            self._in_style_tag = True
            self._style_buffer = []
        updated_attrs = self._rewrite_attrs(tag_lower, attrs)
        self.output.append(self._format_tag(tag, updated_attrs, start_end=False))

    def handle_startendtag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        updated_attrs = self._rewrite_attrs(tag.lower(), attrs)
        self.output.append(self._format_tag(tag, updated_attrs, start_end=True))

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "style":
            css_text = "".join(self._style_buffer)
            if css_text:
                self.output.append(
                    rewrite_inline_css(
                        css_text,
                        self.base_url,
                        self.html_rel_path,
                        self.asset_map,
                        self.css_map,
                    )
                )
            self._style_buffer = []
            self._in_style_tag = False
        self.output.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        if self._in_style_tag:
            self._style_buffer.append(data)
        else:
            self.output.append(data)

    def handle_comment(self, data: str) -> None:
        self.output.append(f"<!--{data}-->")

    def handle_decl(self, decl: str) -> None:
        self.output.append(f"<!{decl}>")

    def handle_entityref(self, name: str) -> None:
        self.output.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        self.output.append(f"&#{name};")

    def unknown_decl(self, data: str) -> None:
        self.output.append(f"<![{data}]>")

    def _rewrite_asset_url(self, value: str) -> str:
        abs_url = normalize_url(resolve_url(self.base_url, value))
        if abs_url in self.asset_map:
            return make_relative_path(self.html_rel_path, self.asset_map[abs_url])
        return value

    def _rewrite_css_url(self, value: str) -> str:
        abs_url = normalize_url(resolve_url(self.base_url, value))
        if abs_url in self.css_map:
            return make_relative_path(self.html_rel_path, self.css_map[abs_url])
        return value

    def _rewrite_srcset(self, value: str) -> str:
        parts = []
        for entry in value.split(","):
            entry = entry.strip()
            if not entry:
                continue
            tokens = entry.split()
            if not tokens:
                continue
            url = tokens[0]
            abs_url = normalize_url(resolve_url(self.base_url, url))
            if abs_url in self.asset_map:
                tokens[0] = make_relative_path(self.html_rel_path, self.asset_map[abs_url])
            parts.append(" ".join(tokens))
        return ", ".join(parts)

    def _format_tag(
        self, tag: str, attrs: List[Tuple[str, Optional[str]]], start_end: bool
    ) -> str:
        rendered = [f"<{tag}"]
        for name, value in attrs:
            if value is None:
                rendered.append(f" {name}")
            else:
                rendered.append(f" {name}=\"{escape(value, quote=True)}\"")
        rendered.append(" />" if start_end else ">")
        return "".join(rendered)

    def _rewrite_attrs(
        self, tag_lower: str, attrs: List[Tuple[str, Optional[str]]]
    ) -> List[Tuple[str, Optional[str]]]:
        attr_map = {name.lower(): value for name, value in attrs if value is not None}
        rel = (attr_map.get("rel") or "").lower()
        as_attr = (attr_map.get("as") or "").lower()
        is_stylesheet = tag_lower == "link" and ("stylesheet" in rel or as_attr == "style")
        is_icon = tag_lower == "link" and ("icon" in rel or "apple-touch-icon" in rel or "mask-icon" in rel)
        is_preload_asset = tag_lower == "link" and "preload" in rel and as_attr in {"image", "font"}
        is_meta_image = tag_lower == "meta" and (
            (attr_map.get("property") or "").lower()
            in {"og:image", "twitter:image", "msapplication-tileimage"}
            or (attr_map.get("name") or "").lower()
            in {"og:image", "twitter:image", "msapplication-tileimage"}
        )

        updated_attrs: List[Tuple[str, Optional[str]]] = []
        for name, value in attrs:
            if value is None:
                updated_attrs.append((name, value))
                continue
            name_lower = name.lower()
            new_value = value
            if name_lower == "src" and tag_lower in {"img", "source"}:
                new_value = self._rewrite_asset_url(value)
            elif name_lower == "srcset" and tag_lower in {"img", "source"}:
                new_value = self._rewrite_srcset(value)
            elif name_lower == "href" and is_stylesheet:
                new_value = self._rewrite_css_url(value)
            elif name_lower == "href" and is_icon:
                new_value = self._rewrite_asset_url(value)
            elif name_lower == "href" and is_preload_asset:
                new_value = self._rewrite_asset_url(value)
            elif name_lower == "content" and is_meta_image:
                new_value = self._rewrite_asset_url(value)
            elif name_lower == "style":
                new_value = rewrite_inline_css(
                    value,
                    self.base_url,
                    self.html_rel_path,
                    self.asset_map,
                    self.css_map,
                )
            updated_attrs.append((name, new_value))
        return updated_attrs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch academy assets and generate a local HTML mirror."
    )
    parser.add_argument(
        "--url",
        default="https://www.mygreatlearning.com/academy",
        help="Page URL to fetch.",
    )
    parser.add_argument(
        "--output-dir",
        default=os.path.join("public", "academy-assets"),
        help="Output directory for assets, CSS, manifest, and HTML.",
    )
    parser.add_argument(
        "--html-out",
        default="academy.html",
        help="Output HTML file name (relative to output dir).",
    )
    parser.add_argument(
        "--manifest",
        default="manifest.json",
        help="Manifest JSON file name (relative to output dir).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List assets without downloading or writing files.",
    )
    parser.add_argument(
        "--allow-domain",
        action="append",
        default=[],
        help="Allow additional domain (can be used multiple times).",
    )
    parser.add_argument(
        "--user-agent",
        default="GL-AcademyAssetFetcher/1.0 (educational use)",
        help="User-Agent header value.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between requests to the same host, in seconds.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=20.0,
        help="Request timeout in seconds.",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Number of retries for transient failures.",
    )
    return parser.parse_args()


def normalize_url(url: Optional[str]) -> str:
    if not url:
        return ""
    url = url.strip()
    if not url:
        return ""
    url, _ = urldefrag(url)
    return url


def resolve_url(base_url: str, value: Optional[str]) -> str:
    if not value:
        return ""
    value = value.strip()
    if not value:
        return ""
    if should_skip_url(value):
        return ""
    return urljoin(base_url, value)


def should_skip_url(value: str) -> bool:
    lowered = value.strip().lower()
    return lowered.startswith("data:") or lowered.startswith("mailto:") or lowered.startswith("javascript:") or lowered.startswith("#")


def parse_srcset(value: str) -> Iterable[str]:
    for entry in value.split(","):
        entry = entry.strip()
        if not entry:
            continue
        parts = entry.split()
        if parts:
            yield parts[0]


def extract_charset(content_type: Optional[str]) -> str:
    if not content_type:
        return "utf-8"
    for part in content_type.split(";"):
        part = part.strip()
        if part.lower().startswith("charset="):
            return part.split("=", 1)[1].strip() or "utf-8"
    return "utf-8"


def is_allowed_domain(url: str, allowed_domains: List[str]) -> bool:
    parsed = urlparse(url)
    host = parsed.hostname or ""
    host = host.lower()
    for domain in allowed_domains:
        domain = domain.lower().lstrip(".")
        if host == domain or host.endswith(f".{domain}"):
            return True
    return False


def is_candidate_asset(url: str) -> bool:
    path = urlparse(url).path
    ext = os.path.splitext(path)[1].lower()
    if ext in ALLOWED_EXTENSIONS:
        return True
    if ext:
        return False
    return True


def extension_from_response(url: str, content_type: Optional[str]) -> Optional[str]:
    path = urlparse(url).path
    ext = os.path.splitext(path)[1].lower()
    if ext in ALLOWED_EXTENSIONS:
        return ext
    if ext:
        return None
    if not content_type:
        return None
    mime = content_type.split(";", 1)[0].strip().lower()
    return MIME_EXTENSION_MAP.get(mime)


def safe_rel_path(url: str, subdir: str, extension: str) -> str:
    parsed = urlparse(url)
    path = parsed.path or "/"
    if path.endswith("/"):
        path = f"{path}index"
    posix_path = posixpath.normpath(path)
    parts = [segment for segment in posix_path.split("/") if segment and segment not in {".", ".."}]
    if not parts:
        parts = ["index"]
    filename = parts[-1]
    base_name = os.path.splitext(filename)[0]
    if parsed.query:
        query_hash = hashlib.sha1(parsed.query.encode("utf-8")).hexdigest()[:8]
        filename = f"{base_name}__q{query_hash}{extension}"
    else:
        filename = f"{base_name}{extension}"
    parts[-1] = filename
    return posixpath.join(subdir, *parts)


def safe_css_rel_path(url: str) -> str:
    path = urlparse(url).path
    ext = os.path.splitext(path)[1].lower()
    if ext != ".css":
        ext = ".css"
    return safe_rel_path(url, "css", ext)


def make_relative_path(from_rel: str, to_rel: str) -> str:
    from_dir = posixpath.dirname(from_rel) or "."
    rel = posixpath.relpath(to_rel, start=from_dir)
    return rel.replace("\\", "/")


def extract_css_links(css_text: str, base_url: str) -> Tuple[Set[str], Set[str]]:
    imports: Set[str] = set()
    assets: Set[str] = set()
    for match in IMPORT_RE.finditer(css_text):
        raw = match.group("url").strip()
        if should_skip_url(raw):
            continue
        abs_url = normalize_url(urljoin(base_url, raw))
        if abs_url:
            imports.add(abs_url)
    for match in URL_RE.finditer(css_text):
        raw = match.group("url").strip()
        if should_skip_url(raw):
            continue
        abs_url = normalize_url(urljoin(base_url, raw))
        if abs_url:
            assets.add(abs_url)
    return imports, assets


def rewrite_css(
    css_text: str,
    css_url: str,
    css_rel_path: str,
    asset_map: Dict[str, str],
    css_map: Dict[str, str],
) -> str:
    def replace_import(match: re.Match) -> str:
        raw = match.group("url").strip()
        if should_skip_url(raw):
            return match.group(0)
        abs_url = normalize_url(urljoin(css_url, raw))
        if abs_url in css_map:
            rel_path = make_relative_path(css_rel_path, css_map[abs_url])
            return f"@import url(\"{rel_path}\")"
        return match.group(0)

    def replace_url(match: re.Match) -> str:
        raw = match.group("url").strip()
        if should_skip_url(raw):
            return match.group(0)
        abs_url = normalize_url(urljoin(css_url, raw))
        if abs_url in asset_map:
            rel_path = make_relative_path(css_rel_path, asset_map[abs_url])
            return f"url(\"{rel_path}\")"
        return match.group(0)

    css_text = IMPORT_RE.sub(replace_import, css_text)
    css_text = URL_RE.sub(replace_url, css_text)
    return css_text


def rewrite_inline_css(
    css_text: str,
    base_url: str,
    html_rel_path: str,
    asset_map: Dict[str, str],
    css_map: Dict[str, str],
) -> str:
    return rewrite_css(css_text, base_url, html_rel_path, asset_map, css_map)


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_bytes(path: Path, data: bytes) -> None:
    ensure_parent(path)
    path.write_bytes(data)


def write_text(path: Path, text: str) -> None:
    ensure_parent(path)
    path.write_text(text, encoding="utf-8")


def run() -> int:
    args = parse_args()
    allowed_domains = ["mygreatlearning.com"] + args.allow_domain

    summary = Summary()
    fetcher = Fetcher(
        user_agent=args.user_agent,
        delay=args.delay,
        timeout=args.timeout,
        retries=args.retries,
    )

    page_result = fetcher.fetch_text(args.url, check_robots=True)
    if page_result.blocked:
        print("Blocked by robots.txt. Exiting.")
        return 1
    if not page_result.ok or not page_result.text:
        print(f"Failed to fetch page: {page_result.error or 'unknown error'}")
        return 1

    base_url = page_result.final_url or args.url
    parser = AssetHtmlParser(base_url)
    parser.feed(page_result.text)

    asset_urls: Set[str] = set(parser.asset_urls)
    css_queue: List[str] = list(parser.css_urls)
    css_seen: Set[str] = set()
    css_content: Dict[str, str] = {}

    while css_queue:
        css_url = normalize_url(css_queue.pop(0))
        if not css_url or css_url in css_seen:
            continue
        css_seen.add(css_url)
        if not is_allowed_domain(css_url, allowed_domains):
            summary.css_skipped_external += 1
            continue
        css_result = fetcher.fetch_text(css_url, check_robots=True)
        if css_result.blocked:
            summary.css_skipped_robots += 1
            continue
        if not css_result.ok or css_result.text is None:
            summary.css_failed += 1
            continue
        summary.css_processed += 1
        css_text = css_result.text
        css_content[css_url] = css_text
        imports, css_assets = extract_css_links(css_text, css_url)
        for import_url in imports:
            if import_url not in css_seen:
                css_queue.append(import_url)
        asset_urls.update(css_assets)

    filtered_assets: List[str] = []
    for url in sorted(asset_urls):
        if not is_allowed_domain(url, allowed_domains):
            summary.assets_skipped_external += 1
            continue
        if not is_candidate_asset(url):
            continue
        filtered_assets.append(url)

    summary.assets_found = len(filtered_assets)

    if args.dry_run:
        print("Assets found:")
        for url in filtered_assets:
            print(url)
        print_summary(summary, args, base_url)
        return 0

    output_dir = Path(args.output_dir)
    assets_dir = output_dir / "assets"
    css_dir = output_dir / "css"
    assets_dir.mkdir(parents=True, exist_ok=True)
    css_dir.mkdir(parents=True, exist_ok=True)

    asset_map: Dict[str, str] = {}
    for url in filtered_assets:
        result = fetcher.fetch_binary(url, check_robots=True)
        if result.blocked:
            summary.assets_skipped_robots += 1
            continue
        if not result.ok or result.data is None:
            summary.assets_failed += 1
            continue
        if result.final_url and not is_allowed_domain(result.final_url, allowed_domains):
            summary.assets_skipped_external += 1
            continue
        extension = extension_from_response(url, result.content_type)
        if not extension:
            summary.assets_failed += 1
            continue
        rel_path = safe_rel_path(url, "assets", extension)
        local_path = output_dir / Path(rel_path)
        write_bytes(local_path, result.data)
        asset_map[url] = rel_path
        summary.assets_downloaded += 1

    css_map: Dict[str, str] = {}
    for css_url in css_content:
        css_rel = safe_css_rel_path(css_url)
        css_map[css_url] = css_rel

    for css_url, css_text in css_content.items():
        css_rel = css_map[css_url]
        rewritten = rewrite_css(css_text, css_url, css_rel, asset_map, css_map)
        write_text(output_dir / Path(css_rel), rewritten)

    html_rel_path = args.html_out
    rewriter = HtmlRewriter(base_url, asset_map, css_map, html_rel_path)
    rewriter.feed(page_result.text)
    rewritten_html = "".join(rewriter.output)
    write_text(output_dir / Path(html_rel_path), rewritten_html)

    manifest_path = output_dir / args.manifest
    manifest_path.write_text(
        json.dumps(asset_map, indent=2, sort_keys=True), encoding="utf-8"
    )

    print_summary(summary, args, base_url, output_dir)
    return 0


def print_summary(
    summary: Summary,
    args: argparse.Namespace,
    base_url: str,
    output_dir: Optional[Path] = None,
) -> None:
    print("\nSummary:")
    print(f"Page: {base_url}")
    print(f"Assets found: {summary.assets_found}")
    print(f"Assets downloaded: {summary.assets_downloaded}")
    print(f"Assets skipped (external): {summary.assets_skipped_external}")
    print(f"Assets skipped (robots): {summary.assets_skipped_robots}")
    print(f"Assets failed: {summary.assets_failed}")
    print(f"CSS processed: {summary.css_processed}")
    print(f"CSS skipped (external): {summary.css_skipped_external}")
    print(f"CSS skipped (robots): {summary.css_skipped_robots}")
    print(f"CSS failed: {summary.css_failed}")
    if output_dir:
        print(f"Output dir: {output_dir}")
        print(f"HTML out: {output_dir / args.html_out}")
        print(f"Manifest: {output_dir / args.manifest}")


if __name__ == "__main__":
    raise SystemExit(run())
