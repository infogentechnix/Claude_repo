"""Tests for free-for-dev/search.py. Run: python3 -m pytest free-for-dev -q"""

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import search  # noqa: E402

SAMPLE = """# free-for.dev

# Table of Contents

  * [Email](#email)

## Email

  * [Mailgun](https://mailgun.com) - 100 emails/day free.
  * [Resend](https://resend.com) - Transactional email API, 3,000 emails/month.

## Web Hosting

  * [Netlify](https://netlify.com) - Static hosting, 100 GB bandwidth.
    * Continuation line about Netlify functions.
"""


@pytest.fixture
def entries():
    return search.parse(SAMPLE)


def test_parse_skips_table_of_contents(entries):
    assert [e.name for e in entries] == ["Mailgun", "Resend", "Netlify"]


def test_parse_records_section_url_and_continuation(entries):
    netlify = entries[-1]
    assert netlify.section == "Web Hosting"
    assert netlify.url == "https://netlify.com"
    assert "functions" in netlify.description


def test_nested_linked_bullet_becomes_its_own_entry():
    text = (
        "## Major Cloud Providers\n\n"
        "  * Google Cloud Platform\n"
        "    * [App Engine](https://cloud.google.com/appengine) - 28 instance hours/day\n"
        "  * [Vercel](https://vercel.com) - Hosting\n"
        "    * [Functions](https://vercel.com/fn) - 100k calls\n"
    )
    found = search.parse(text)
    assert [e.name for e in found] == ["Google Cloud Platform › App Engine", "Vercel", "Vercel › Functions"]


def test_search_requires_every_term_case_insensitive(entries):
    hits = search.search(entries, ["EMAIL", "api"])
    assert [e.name for e in hits] == ["Resend"]


def test_search_filters_by_section_substring(entries):
    hits = search.search(entries, [], section="hosting")
    assert [e.name for e in hits] == ["Netlify"]


def test_search_returns_empty_when_nothing_matches(entries):
    assert search.search(entries, ["kubernetes"]) == []


def test_sections_counts_entries(entries):
    assert search.sections(entries) == [("Email", 2), ("Web Hosting", 1)]


def test_cli_runs_against_vendored_list():
    script = Path(__file__).parent / "search.py"
    out = subprocess.run(
        [sys.executable, "-I", str(script), "--section", "email", "--limit", "3"],
        capture_output=True, text=True, check=True,
    ).stdout
    assert "[Email]" in out
