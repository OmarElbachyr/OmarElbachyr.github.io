#!/usr/bin/env python
"""Sync this site's publications and citation cache from its Scholar profile."""

import os
from pathlib import Path
import re
import sys
import tempfile
import unicodedata
from datetime import datetime
from zoneinfo import ZoneInfo

import yaml
import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from scholarly import scholarly

CONFIG_FILE = Path("_data/socials.yml")
OUTPUT_FILE = Path("_data/citations.yml")
BIBLIOGRAPHY_FILE = Path("_bibliography/papers.bib")


def load_scholar_user_id() -> str:
    with CONFIG_FILE.open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream) or {}
    scholar_user_id = config.get("scholar_userid")
    if not isinstance(scholar_user_id, str) or not scholar_user_id.strip():
        raise ValueError("Add your Google Scholar user ID to _data/socials.yml.")
    return scholar_user_id.strip()


def fetch_citation_counts(scholar_user_id: str) -> tuple[dict, dict]:
    """Read profile counts without querying citing papers or estimating values."""
    scholarly.set_timeout(15)
    scholarly.set_retries(3)
    author = scholarly.search_author_id(scholar_user_id)
    author_data = scholarly.fill(author, sections=["publications"])
    publications = author_data.get("publications") if author_data else None
    if not isinstance(publications, list) or not publications:
        raise ValueError("Scholar returned no publications; keeping saved counts.")

    papers = {}
    records = {}
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
            raise ValueError(
                "Scholar returned incomplete publication data; keeping saved counts."
            )
        if ":" not in publication_id:
            publication_id = f"{scholar_user_id}:{publication_id}"
        if not re.fullmatch(
            re.escape(scholar_user_id) + r":[A-Za-z0-9_-]+", publication_id
        ):
            raise ValueError(
                "Scholar returned an invalid publication ID or a different author."
            )
        if publication_id in papers:
            raise ValueError("Scholar returned duplicate publication IDs.")
        papers[publication_id] = {
            "title": title,
            "year": str(publication.get("bib", {}).get("pub_year") or "Unknown Year"),
            "citations": citations,
        }
        records[publication_id] = publication
        print(f"Found: {title} - Citations: {citations}")
    return papers, records


def normalized_title(title: str) -> str:
    """Match curated BibTeX titles despite capitalization, braces and punctuation."""
    title = unicodedata.normalize("NFKC", title).casefold()
    return "".join(character for character in title if character.isalnum())


def latex_text(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "{": r"\{",
        "}": r"\}",
        "$": r"\$",
        "&": r"\&",
        "#": r"\#",
        "%": r"\%",
        "_": r"\_",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(character, character) for character in value)


def sync_bibliography(source: str, papers: dict, records: dict) -> str:
    """Append new papers and link existing ones without rewriting curated entries."""
    # This site's bibliography has Jekyll front matter, which is not BibTeX.
    bibliography = re.sub(
        r"\A---\r?\n.*?\r?\n---\r?\n|\A---\r?\n---\r?\n",
        "",
        source,
        count=1,
        flags=re.S,
    )
    entries = bibtexparser.loads(bibliography).entries
    by_id = {}
    by_title = {}
    keys = {entry["ID"] for entry in entries}
    for entry in entries:
        scholar_id = entry.get("google_scholar_id", "").split(":")[-1]
        if scholar_id:
            if scholar_id in by_id:
                raise ValueError("Duplicate Scholar IDs in the bibliography.")
            by_id[scholar_id] = entry
        by_title.setdefault(normalized_title(entry.get("title", "")), []).append(entry)

    for publication_id in papers:
        short_id = publication_id.split(":", 1)[1]
        if short_id in by_id:
            continue
        # Full records provide complete titles and author names, unlike profile snippets.
        record = scholarly.fill(records[publication_id])
        bib = record.get("bib", {})
        title = bib.get("title", "").strip()
        author = bib.get("author", "")
        if isinstance(author, list):
            author = " and ".join(author)
        if (
            not title
            or not isinstance(author, str)
            or not author.strip()
            or "…" in title
        ):
            raise ValueError(
                f"Incomplete metadata for {publication_id}; keeping saved files."
            )
        matches = by_title.get(normalized_title(title), [])
        if len(matches) > 1:
            raise ValueError(f"Ambiguous bibliography title: {title}")
        if matches:
            entry = matches[0]
            if entry.get("google_scholar_id"):
                raise ValueError(f"Conflicting Scholar IDs for {title}")
            # Insert only the ID; leave every manually edited field byte-for-byte intact.
            pattern = r"(@\w+\s*\{\s*" + re.escape(entry["ID"]) + r"\s*,)"
            source, count = re.subn(
                pattern,
                lambda match: match[1] + f"\n  google_scholar_id = {{{short_id}}},",
                source,
                count=1,
            )
            if count != 1:
                raise ValueError(f"Cannot locate bibliography entry {entry['ID']}")
            entry["google_scholar_id"] = short_id
            by_id[short_id] = entry
            print(f"Linked existing paper: {title}")
            continue

        key = "scholar_" + short_id
        if key in keys:
            raise ValueError(f"Bibliography key collision: {key}")
        entry = {
            "ENTRYTYPE": (
                "article"
                if bib.get("journal")
                else "inproceedings" if bib.get("conference") else "misc"
            ),
            "ID": key,
            "title": "{" + latex_text(title) + "}",
            "author": latex_text(author),
            "google_scholar_id": short_id,
            "selected": "true",
        }
        for field, target in (
            ("pub_year", "year"),
            ("journal", "journal"),
            ("conference", "booktitle"),
            ("volume", "volume"),
            ("number", "number"),
            ("pages", "pages"),
            ("publisher", "publisher"),
            ("abstract", "abstract"),
        ):
            if bib.get(field):
                entry[target] = latex_text(str(bib[field]))
        url = record.get("pub_url", "")
        if isinstance(url, str) and url.startswith(("https://", "http://")):
            entry["html"] = url.replace("{", "%7B").replace("}", "%7D")
        database = BibDatabase()
        database.entries = [entry]
        source = source.rstrip() + "\n\n" + bibtexparser.dumps(database)
        keys.add(key)
        by_id[short_id] = entry
        by_title.setdefault(normalized_title(title), []).append(entry)
        print(f"Added new paper: {title}")
    return source


def atomic_write(path: Path, content: str) -> None:
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, delete=False
        ) as stream:
            temporary_path = Path(stream.name)
            stream.write(content)
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


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
    papers, records = fetch_citation_counts(scholar_user_id)
    bibliography = BIBLIOGRAPHY_FILE.read_text(encoding="utf-8")
    updated_bibliography = sync_bibliography(bibliography, papers, records)
    counts_changed = existing_data.get("papers") != papers
    if not counts_changed and bibliography == updated_bibliography:
        print("No changes in publications or citations. Skipping file update.")
        return False

    citation_data = {
        "metadata": {
            "last_updated": datetime.now(ZoneInfo("Europe/Luxembourg"))
            .date()
            .isoformat()
        },
        "papers": papers,
    }
    # Finish fetching and validating every new paper before touching either file.
    if bibliography != updated_bibliography:
        atomic_write(BIBLIOGRAPHY_FILE, updated_bibliography)
    if counts_changed:
        atomic_write(
            OUTPUT_FILE,
            yaml.safe_dump(
                citation_data, allow_unicode=True, width=1000, sort_keys=True
            ),
        )
    print("Scholar publications and citations synchronized.")
    return True


if __name__ == "__main__":
    try:
        get_scholar_citations()
    except Exception as error:
        print(f"Citation update failed: {error}", file=sys.stderr)
        sys.exit(1)
