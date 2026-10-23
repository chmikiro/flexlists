#!/usr/bin/env python3
"""Tests for make_foxyproxy_list.py (stdlib unittest, no third-party deps)."""
import sys
import tempfile
import unittest
import io
import contextlib
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import make_foxyproxy_list as m  # noqa: E402

PROXIES = REPO_ROOT / "proxies.txt"
COUNTRY_CSV = REPO_ROOT / "country_names.csv"


class TestLoadOverrides(unittest.TestCase):
    def test_parses_three_columns(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
            f.write("Europe/Kyiv,UA,Ukraine\n")
            path = f.name
        try:
            self.assertEqual(m.load_overrides(path), {"Europe/Kyiv": ("UA", "Ukraine")})
        finally:
            Path(path).unlink()

    def test_skips_header_blank_and_comments(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
            f.write("timezone,cc,country\n# a comment\n\nEurope/Kyiv,UA,Ukraine\n")
            path = f.name
        try:
            self.assertEqual(m.load_overrides(path), {"Europe/Kyiv": ("UA", "Ukraine")})
        finally:
            Path(path).unlink()

    def test_shipped_csv_loads_without_error(self):
        # Regression: the committed country_names.csv must parse.
        over = m.load_overrides(str(COUNTRY_CSV))
        self.assertEqual(over["Europe/London"], ("GB", "United Kingdom"))


class TestLoadTz(unittest.TestCase):
    def test_mappings_present(self):
        names, zones = m.load_tz(m.find_tzdir())
        self.assertEqual(zones["Europe/London"], "GB")
        self.assertIn("GB", names)


class TestMain(unittest.TestCase):
    def _run(self, args, out):
        with mock.patch.object(sys, "argv", ["make_foxyproxy_list.py", *args]), \
             contextlib.redirect_stdout(io.StringIO()):
            m.main()
        return Path(out).read_text().splitlines()

    def test_full_output_line_count_and_format(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "all.txt"
            lines = self._run([str(PROXIES), str(out), "--tzdir", str(m.find_tzdir())], str(out))
            self.assertEqual(len(lines), 532)
            first = lines[0]
            self.assertTrue(first.startswith("socks5://"))
            self.assertIn("title=", first)
            self.assertIn("&cc=", first)
            self.assertIn("&country=", first)

    def test_region_filter_europe(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "eu.txt"
            lines = self._run(
                [str(PROXIES), str(out), "--region", "Europe", "--tzdir", str(m.find_tzdir())],
                str(out),
            )
            self.assertEqual(len(lines), 216)
            self.assertTrue(all("&cc=" in l and "&cc=EU" not in l for l in lines))

    def test_map_override_applied(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "all.txt"
            lines = self._run(
                [
                    str(PROXIES),
                    str(out),
                    "--map",
                    str(COUNTRY_CSV),
                    "--tzdir",
                    str(m.find_tzdir()),
                ],
                str(out),
            )
            gb = [l for l in lines if "&cc=GB&" in l]
            self.assertTrue(gb)
            self.assertTrue(all("country=United%20Kingdom" in l for l in gb))

    def test_missing_timezone_exits_nonzero(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "bad.txt"
            src.write_text("1.2.3.4 Not/A_Zone\n")
            out = Path(d) / "out.txt"
            with self.assertRaises(SystemExit) as cm:
                self._run([str(src), str(out), "--tzdir", str(m.find_tzdir())], str(out))
            self.assertIn("No country for", str(cm.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2)