#!/usr/bin/env python
"""Refresh the site's cached counts from its Google Scholar author profile."""

import os
from pathlib import Path
import sys
import tempfile
from datetime import datetime
from zoneinfo import ZoneInfo

import yaml
from scholarly import scholarly

CONFIG_FILE = Path("_data/socials.yml")
OUTPUT_FILE = Path("_data/citations.yml")


def load_scholar_user_id() -> str:
    with CONFIG_FILE.open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream) or {}
    scholar_user_id = config.get("scholar_userid")
    if not isinstance(scholar_user_id, str) or not scholar_user_id.strip():
        raise ValueError("Add your Google Scholar user ID to _data/socials.yml.")
    return scholar_user_id.strip()


def fetch_citation_counts(scholar_user_id: str) -> dict:
    """Read profile counts without querying citing papers or estimating values."""
    scholarly.set_timeout(15)
    scholarly.set_retries(3)
    author = scholarly.search_author_id(scholar_user_id)
    author_data = scholarly.fill(author, sections=["publications"])
    publications = author_data.get("publications") if author_data else None
    if not isinstance(publications, list) or not publications:
        raise ValueError("Scholar returned no publications; keeping saved counts.")

    papers = {}
    for publication in publications:
        publication_id = publication.get("author_pub_id") or publication.get("pub_id")
        title = publication.get("bib", {}).get("title")
        citations = publication.get("num_citations")
        # Missing or malformed counts must never silently become zero.
        if (
            not isinstance(publication_id, str)
            or not publication_id
            or not isinstance(title, str)
            or not title.strip()
            or type(citations) is not int
            or citations < 0
        ):
            raise ValueError("Scholar returned incomplete publication data; keeping saved counts.")
        if ":" not in publication_id:
            publication_id = f"{scholar_user_id}:{publication_id}"
        if not publication_id.startswith(f"{scholar_user_id}:"):
            raise ValueError("Scholar returned a publication for a different author.")
        if publication_id in papers:
            raise ValueError("Scholar returned duplicate publication IDs.")
        papers[publication_id] = {
            "title": title,
            "year": str(publication.get("bib", {}).get("pub_year") or "Unknown Year"),
            "citations": citations,
        }
        print(f"Found: {title} - Citations: {citations}")
    return papers


def get_scholar_citations() -> bool:
    """Write only a complete, changed result; leave the cache intact on failure."""
    scholar_user_id = load_scholar_user_id()
    existing_data = {}
    if OUTPUT_FILE.exists():
        with OUTPUT_FILE.open(encoding="utf-8") as stream:
            existing_data = yaml.safe_load(stream) or {}
        if not isinstance(existing_data, dict):
            raise ValueError("The citation cache must contain a YAML mapping.")

    print(f"Fetching citations for Google Scholar ID: {scholar_user_id}")
    # Always fetch, including manual reruns on a day that already has an update.
    papers = fetch_citation_counts(scholar_user_id)
    if existing_data.get("papers") == papers:
        print("No changes in citation data. Skipping file update.")
        return False

    citation_data = {
        "metadata": {
            "last_updated": datetime.now(ZoneInfo("Europe/Luxembourg")).date().isoformat()
        },
        "papers": papers,
    }
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=OUTPUT_FILE.parent, delete=False
        ) as stream:
            temporary_path = Path(stream.name)
            yaml.safe_dump(
                citation_data, stream, allow_unicode=True, width=1000, sort_keys=True
            )
        os.replace(temporary_path, OUTPUT_FILE)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
    print(f"Citation data saved to {OUTPUT_FILE}")
    return True


if __name__ == "__main__":
    try:
        get_scholar_citations()
    except Exception as error:
        print(f"Citation update failed: {error}", file=sys.stderr)
        sys.exit(1)
