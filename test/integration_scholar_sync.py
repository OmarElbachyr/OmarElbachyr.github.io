"""Exercise the site's Scholar-to-BibTeX/cache workflow without network requests.

Run: python -m unittest discover -s test -p integration_scholar_sync.py
"""

import copy
import importlib.util
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

import bibtexparser
import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "scholar_sync", ROOT / "bin/update_scholar_citations.py"
)
sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync)
AUTHOR = "k9z_ASsAAAAJ"


def publication(short_id, title, citations=0):
    return {
        "author_pub_id": f"{AUTHOR}:{short_id}",
        "num_citations": citations,
        "bib": {
            "title": title,
            "author": "El Bachyr, Omar and Doe, Jane",
            "pub_year": "2026",
        },
    }


class ScholarSyncIntegration(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        directory = Path(self.directory.name)
        self.bib = directory / "papers.bib"
        self.cache = directory / "citations.yml"
        self.config = directory / "socials.yml"
        self.original = (ROOT / "_bibliography/papers.bib").read_text(encoding="utf-8")
        self.bib.write_text(self.original, encoding="utf-8")
        self.cache.write_text("metadata: {last_updated: '2026-10-22'}\npapers: {}\n")
        self.config.write_text(f"scholar_userid: {AUTHOR}\n")
        for name, value in (
            ("BIBLIOGRAPHY_FILE", self.bib),
            ("OUTPUT_FILE", self.cache),
            ("CONFIG_FILE", self.config),
        ):
            mock = patch.object(sync, name, value)
            mock.start()
            self.addCleanup(mock.stop)

    def run_sync(self, records, details=None):
        def fill(record, **kwargs):
            if "sections" in kwargs:
                return {"publications": copy.deepcopy(records)}
            return (details or {}).get(record["author_pub_id"], record)

        with patch.object(
            sync.scholarly, "search_author_id", return_value={}
        ), patch.object(sync.scholarly, "fill", side_effect=fill) as mocked:
            result = sync.get_scholar_citations()
        return result, mocked

    def test_new_paper_import_preserves_curated_entries_and_zero_citations(self):
        record = publication("newPaper", "A {test}: 100% R&D with $x_y$")
        record["bib"].update(
            conference="Research & Development", abstract="A complete abstract."
        )
        record["pub_url"] = "https://example.org/paper"
        changed, _ = self.run_sync([record])
        self.assertTrue(changed)
        self.assertTrue(self.bib.read_text().startswith(self.original.rstrip()))
        entries = bibtexparser.loads(self.bib.read_text().split("---", 2)[2]).entries
        entry = next(entry for entry in entries if entry["ID"] == "scholar_newPaper")
        self.assertEqual(entry["ENTRYTYPE"], "inproceedings")
        self.assertEqual(entry["google_scholar_id"], "newPaper")
        self.assertEqual(entry["selected"], "true")
        self.assertEqual(entry["html"], "https://example.org/paper")
        self.assertIn(r"100\% R\&D", entry["title"])
        self.assertEqual(
            yaml.safe_load(self.cache.read_text())["papers"][f"{AUTHOR}:newPaper"][
                "citations"
            ],
            0,
        )
        before = (self.bib.read_bytes(), self.cache.read_bytes())
        changed, mocked = self.run_sync([record])
        self.assertFalse(changed)
        self.assertEqual(mocked.call_count, 1)  # No repeat publication detail requests.
        self.assertEqual(before, (self.bib.read_bytes(), self.cache.read_bytes()))

    def test_existing_ragit_is_linked_without_duplicate_or_lost_custom_fields(self):
        # Keep this scenario stable after a real sync has already linked RAGit.
        prefix, remainder = self.original.split("@inproceedings{elbachyr2026ragit,", 1)
        body, suffix = remainder.split("\n}", 1)
        body = re.sub(r"\n\s*google_scholar_id\s*=\s*\{[^}]*\},?", "", body)
        self.original = (
            prefix + "@inproceedings{elbachyr2026ragit," + body + "\n}" + suffix
        )
        self.bib.write_text(self.original, encoding="utf-8")
        title = "RAGit: Turning Document Preprocessing into an Experimental Variable for RAG"
        record = publication("ragitId", title, 3)
        self.run_sync([record])
        expected = self.original.replace(
            "@inproceedings{elbachyr2026ragit,",
            "@inproceedings{elbachyr2026ragit,\n  google_scholar_id = {ragitId},",
        )
        self.assertEqual(self.bib.read_text(), expected)

    def test_citations_refresh_without_rewriting_bibliography(self):
        record = publication("2osOgNQ5qMEC", "LëtzCross", 9)
        _, mocked = self.run_sync([record])
        self.assertEqual(mocked.call_count, 1)
        self.assertEqual(self.bib.read_text(), self.original)
        self.assertEqual(
            yaml.safe_load(self.cache.read_text())["papers"][f"{AUTHOR}:2osOgNQ5qMEC"][
                "citations"
            ],
            9,
        )

    def test_detail_failure_after_first_import_leaves_both_files_intact(self):
        first = publication("first", "First new paper")
        incomplete = publication("incomplete", "Incomplete paper")
        incomplete["bib"].pop("author")
        before = (self.bib.read_bytes(), self.cache.read_bytes())
        with self.assertRaisesRegex(ValueError, "Incomplete metadata"):
            self.run_sync([first, incomplete])
        self.assertEqual(before, (self.bib.read_bytes(), self.cache.read_bytes()))

    def test_bad_profile_responses_leave_both_files_intact(self):
        missing_count = publication("missing", "Missing count")
        missing_count.pop("num_citations")
        duplicate = publication("same", "Duplicated paper")
        wrong_author = publication("wrong", "Wrong author")
        wrong_author["author_pub_id"] = "someoneElse:wrong"
        before = (self.bib.read_bytes(), self.cache.read_bytes())
        for records in ([], [missing_count], [duplicate, duplicate], [wrong_author]):
            with self.subTest(records=records), self.assertRaises(ValueError):
                self.run_sync(records)
            self.assertEqual(before, (self.bib.read_bytes(), self.cache.read_bytes()))


if __name__ == "__main__":
    unittest.main()
