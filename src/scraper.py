from __future__ import annotations

"""
Phase 1 implementation: Stealth scraper for the Groww Mutual Fund FAQ Assistant.
...
"""

import sys
import asyncio

if sys.platform == 'win32':
    try:
        if not isinstance(asyncio.get_event_loop_policy(), asyncio.WindowsProactorEventLoopPolicy):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        pass

from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin
import json
import re

import logging

from bs4 import BeautifulSoup
from playwright.sync_api import Browser, BrowserContext, Playwright, sync_playwright
from playwright_stealth import Stealth

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

CONFIG_PATH = Path("config") / "sources.json"
RAW_DATA_ROOT = Path("data") / "raw"
_STEALTH = Stealth()


@dataclass
class SourceConfig:
    """Represents a single entry from `config/sources.json`."""

    name: str
    category: str
    url: str
    enabled: bool = True
    type: str = "fund_page"  # e.g. "overview", "fund_page", "fof_page", "etf_page"


@dataclass
class ScrapedArtifact:
    """
    Describes one saved artifact from the scraper run.

    Each artifact must be traceable back to its `source_url` for RAG citations.
    """

    path: Path
    source_url: str
    content_type: str  # e.g. "html", "pdf"
    fetched_at: datetime


def _slugify(name: str) -> str:
    """Convert a scheme name into a filesystem-friendly slug."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name).strip("-").lower()
    return slug or "page"


def load_sources(config_path: Path = CONFIG_PATH) -> List[SourceConfig]:
    """
    Load and parse the Groww sources configuration.

    Expected JSON shape:
        { "sources": [ { "name": ..., "category": ..., "url": ..., "enabled": true, "type": ... }, ... ] }

    Returns a list of `SourceConfig` objects for all enabled sources.
    """
    with config_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    sources: List[SourceConfig] = []
    for entry in raw.get("sources", []):
        if not entry.get("enabled", True):
            continue
        sources.append(
            SourceConfig(
                name=entry["name"],
                category=entry.get("category", "Unknown"),
                url=entry["url"],
                enabled=entry.get("enabled", True),
                type=entry.get("type", "fund_page"),
            )
        )
    return sources


def get_run_output_dir(run_date: Optional[date] = None) -> Path:
    """
    Determine (and create) the output directory for a given run, e.g. `data/raw/2026-03-06/`.
    """
    if run_date is None:
        run_date = date.today()
    run_dir = RAW_DATA_ROOT / run_date.isoformat()
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def launch_browser_stealth() -> Tuple[Playwright, Browser, BrowserContext]:
    """
    Prepare and return a Playwright browser context configured for stealth usage.
    """
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={"width": 1280, "height": 720},
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
    )
    return p, browser, context


def scrape_page_html(context: BrowserContext, source: SourceConfig, output_dir: Path) -> ScrapedArtifact:
    """
    Visit `source.url` using the provided Playwright context and save an HTML snapshot.
    """
    page = context.new_page()
    _STEALTH.apply_stealth_sync(page)

    page.goto(source.url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(3000) # Give it 3s to hydrate React DOM
    html = page.content()

    slug = _slugify(source.name)
    html_path = output_dir / f"{slug}.html"
    html_path.write_text(html, encoding="utf-8")

    return ScrapedArtifact(
        path=html_path,
        source_url=source.url,
        content_type="html",
        fetched_at=datetime.now(tz=timezone.utc),
    )


def discover_and_download_pdfs(
    context: BrowserContext, source: SourceConfig, output_dir: Path
) -> List[ScrapedArtifact]:
    """
    Discover outbound links to PDFs on the Groww page and download them.

    Every downloaded PDF is recorded with `source_url` pointing to the originating Groww page.
    """
    page = context.new_page()
    _STEALTH.apply_stealth_sync(page)

    page.goto(source.url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(3000) # Give it 3s to hydrate React DOM
    html = page.content()

    soup = BeautifulSoup(html, "html.parser")
    pdf_links: List[str] = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if ".pdf" in href.lower():
            pdf_links.append(urljoin(source.url, href))

    artifacts: List[ScrapedArtifact] = []
    for idx, pdf_url in enumerate(sorted(set(pdf_links))):
        response = context.request.get(pdf_url)
        if not response.ok:
            continue

        slug = _slugify(source.name)
        pdf_filename = f"{slug}-doc-{idx + 1}.pdf"
        pdf_path = output_dir / pdf_filename
        pdf_path.write_bytes(response.body())

        artifacts.append(
            ScrapedArtifact(
                path=pdf_path,
                source_url=source.url,
                content_type="pdf",
                fetched_at=datetime.now(tz=timezone.utc),
            )
        )

    return artifacts


def write_manifest(artifacts: List[ScrapedArtifact], output_dir: Path, run_date: date) -> Path:
    """
    Serialize all scraped artifacts for this run into a `manifest.json` file.
    """
    manifest_path = output_dir / "manifest.json"

    manifest: Dict[str, Any] = {
        "run_date": run_date.isoformat(),
        "artifacts": [],
    }

    for artifact in artifacts:
        record = asdict(artifact)
        record["path"] = str(artifact.path.as_posix())
        record["fetched_at"] = artifact.fetched_at.isoformat() + "Z"
        record["run_date"] = run_date.isoformat()
        manifest["artifacts"].append(record)

    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return manifest_path


def fetch_daily(run_date: Optional[date] = None) -> Dict[str, Any]:
    """
    Orchestrate a single daily scrape of all enabled Groww sources.
    """
    if run_date is None:
        run_date = date.today()

    output_dir = get_run_output_dir(run_date)
    sources = load_sources()

    all_artifacts: List[ScrapedArtifact] = []

    p: Optional[Playwright] = None
    browser: Optional[Browser] = None
    context: Optional[BrowserContext] = None

    try:
        p, browser, context = launch_browser_stealth()

        total = len(sources)
        for idx, source in enumerate(sources, start=1):
            logger.info(f"[{idx}/{total}] Scraping: {source.name} ({source.url})")
            try:
                html_artifact = scrape_page_html(context, source, output_dir)
                all_artifacts.append(html_artifact)
                logger.info(f"  ✓ HTML saved: {html_artifact.path.name}")

                pdf_artifacts = discover_and_download_pdfs(context, source, output_dir)
                all_artifacts.extend(pdf_artifacts)
                if pdf_artifacts:
                    logger.info(f"  ✓ PDFs saved: {[a.path.name for a in pdf_artifacts]}")
            except Exception as e:
                logger.warning(f"  ✗ Failed {source.name}: {e}")

    finally:
        if context is not None:
            context.close()
        if browser is not None:
            browser.close()
        if p is not None:
            p.stop()

    manifest_path = write_manifest(all_artifacts, output_dir, run_date)

    return {
        "run_date": run_date.isoformat(),
        "output_dir": str(output_dir.as_posix()),
        "artifact_count": len(all_artifacts),
        "manifest_path": str(manifest_path.as_posix()),
    }


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    summary = fetch_daily()
    print(json.dumps(summary, indent=2))
