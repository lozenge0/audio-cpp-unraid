"""Local publication guardrails, not a secret scanner or publishing tool."""
from pathlib import Path
import re
import subprocess
import unittest
from scripts.check_publication import PUBLIC_FILES, scan_content

ROOT = Path(__file__).resolve().parents[1]


def candidate_files():
    """Tracked files plus untracked files Git would not ignore.

    Ignored caches such as __pycache__ and .pytest_cache never appear, while a
    stray untracked file still fails the inventory before it is committed.
    """
    output = subprocess.run(
        ['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'],
        cwd=ROOT, check=True, capture_output=True, text=True).stdout
    return {name for name in output.split('\0') if name}
EXPECTED = PUBLIC_FILES


class PublicationTests(unittest.TestCase):
    def test_first_time_guide_keeps_safety_and_routes_advanced_notes(self):
        readme = (ROOT / 'README.md').read_text()
        config = (ROOT / 'docs/CONFIGURATION.md').read_text()
        maintainer = (ROOT / 'docs/MAINTAINER.md').read_text()
        for heading in ('## What can I use it for?', '## Install on Unraid',
                        '## Make your first speech sample', '## Security',
                        '## Already installed?'):
            self.assertIn(heading, readme)
        self.assertIn('(docs/RELEASE-REVIEW.md)', readme)
        self.assertIn('(docs/CONFIGURATION.md)', readme)
        self.assertIn('(docs/MAINTAINER.md)', readme)
        # Tuning flags stay out of the first-time guide.
        self.assertNotIn('--max-loaded-models', readme)
        self.assertIn('--max-loaded-models', config)
        self.assertIn('python3 -m unittest discover -s tests', maintainer)

    def test_approved_licence_scopes(self):
        licence = (ROOT / 'LICENSE').read_text()
        artwork = (ROOT / 'assets/README.md').read_text()
        readme = (ROOT / 'README.md').read_text()
        self.assertTrue(licence.startswith('MIT License\n'))
        self.assertIn('CC0-1.0', artwork)
        self.assertIn('https://creativecommons.org/publicdomain/zero/1.0/legalcode.en', artwork)
        self.assertIn('CC0', readme)
        self.assertIn('(assets/README.md)', readme)

    def test_exact_candidate_inventory(self):
        actual = candidate_files()
        for name in sorted(actual):
            path = ROOT / name
            self.assertFalse(path.is_symlink(), f'Unexpected symlink: {name}')
            self.assertTrue(path.is_file(), f'Tracked file missing: {name}')
        self.assertEqual(actual, EXPECTED,
                         'Review unexpected files before expanding the publication list')

    def test_relative_markdown_links_stay_inside_candidate(self):
        for name in sorted(EXPECTED):
            if not name.endswith('.md'):
                continue
            path = ROOT / name
            for link in re.findall(r'\]\(([^)]+)\)', path.read_text()):
                if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', link) or link.startswith('#'):
                    continue
                target = (path.parent / link.split('#', 1)[0]).resolve()
                with self.subTest(file=name, link=link):
                    self.assertIn(ROOT, target.parents)
                    self.assertTrue(target.is_file())

    def test_no_selected_private_data_patterns_in_public_content(self):
        for name in sorted(EXPECTED):
            with self.subTest(file=name):
                self.assertEqual(scan_content(name, (ROOT / name).read_bytes()), set())


if __name__ == '__main__':
    unittest.main()
