"""Local publication guardrails, not a secret scanner or publishing tool."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    '.github/dependabot.yml', '.github/workflows/validate.yml',
    '.gitignore', 'CHANGELOG.md', 'LICENSE', 'README.md',
    'CONTRIBUTING.md', 'SECURITY.md',
    'assets/README.md', 'assets/icon.svg', 'ca_profile.xml',
    'docs/CONFIGURATION.md', 'docs/MAINTAINER.md',
    'docs/CPU-RETEST-20260912.md', 'docs/FIRST-RUN-FINDINGS.md',
    'docs/PLAN.md', 'docs/PUBLISHING.md', 'docs/RECREATION-TEST.md', 'docs/RELEASE-REVIEW.md',
    'docs/SHORT-TEXT-INVESTIGATION.md', 'docs/UI-TEST-PREFLIGHT.md',
    'docs/UPDATE-ROLLBACK-TEST.md', 'docs/USER-IDENTITY-TESTS.md',
    'docs/VALIDATION.md', 'templates/audio-cpp.xml',
    'tests/test_ci.py', 'tests/test_publication.py', 'tests/test_template.py',
}


class PublicationTests(unittest.TestCase):
    def test_first_time_guide_keeps_safety_and_routes_advanced_notes(self):
        readme = (ROOT / 'README.md').read_text()
        config = (ROOT / 'docs/CONFIGURATION.md').read_text()
        maintainer = (ROOT / 'docs/MAINTAINER.md').read_text()
        for heading in ('## What can I use it for?', '## Install on Unraid',
                        '## Make your first speech sample', '## Security'):
            self.assertIn(heading, readme)
        self.assertIn('no login or API authentication', readme)
        self.assertIn('public-listing installation checks are still in progress', readme)
        self.assertIn('(docs/CONFIGURATION.md)', readme)
        self.assertIn('(docs/MAINTAINER.md)', readme)
        self.assertNotIn('--max-loaded-models', readme)
        self.assertIn('--max-loaded-models', config)
        self.assertIn('not yet been integration-tested', config)
        self.assertIn('Run from the repository root', maintainer)

    def test_approved_licence_scopes(self):
        licence = (ROOT / 'LICENSE').read_text()
        artwork = (ROOT / 'assets/README.md').read_text()
        readme = (ROOT / 'README.md').read_text()
        self.assertTrue(licence.startswith('MIT License\n'))
        self.assertIn('CC0-1.0', artwork)
        self.assertIn('https://creativecommons.org/publicdomain/zero/1.0/legalcode.en', artwork)
        self.assertIn('to the extent they hold copyright and related rights', artwork)
        self.assertIn('The icon is separately dedicated under CC0', readme)

    def test_exact_candidate_inventory(self):
        actual = set()
        for path in ROOT.rglob('*'):
            rel = path.relative_to(ROOT)
            self.assertFalse(path.is_symlink(), f'Unexpected symlink: {rel}')
            if rel.parts[0] == '.git':
                continue  # Only the standalone repository's root Git metadata.
            if rel.as_posix() == 'tests/__pycache__' and path.is_dir():
                continue
            if len(rel.parts) == 3 and rel.parts[:2] == ('tests', '__pycache__'):
                cache = re.fullmatch(r'(test_\w+)\.cpython-\d+\.pyc', rel.name)
                self.assertTrue(path.is_file() and cache,
                                f'Unexpected cache content: {rel}')
                self.assertIn(f'tests/{cache.group(1)}.py', EXPECTED)
                continue
            if path.is_file():
                actual.add(rel.as_posix())
        self.assertEqual(actual, EXPECTED,
                         'Review unexpected files before expanding the publication list')

    def test_review_lists_exact_candidate(self):
        review = (ROOT / 'docs/RELEASE-REVIEW.md').read_text()
        manifest = re.search(r'```text\n(.*?)\n```', review, re.DOTALL)
        self.assertIsNotNone(manifest)
        entries = manifest.group(1).splitlines()
        self.assertEqual(len(entries), len(set(entries)))
        self.assertEqual(set(entries), EXPECTED)

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
        # Tests themselves contain negative examples. SVG metadata is preserved;
        # this plain-text check does not decode/clear provenance metadata.
        patterns = (
            r'/Users/', r'192\.168\.\d{1,3}\.\d{1,3}',
            r'GPU-[0-9a-fA-F]{8}-',
            r'-----BEGIN (?:OPENSSH |RSA |EC )?PRIVATE KEY-----',
            r'\bgh[pousr]_[A-Za-z0-9]{30,}\b',
            r'\bgithub_pat_[A-Za-z0-9_]{30,}\b',
        )
        for name in sorted(EXPECTED):
            if name.startswith('tests/'):
                continue
            text = (ROOT / name).read_text()
            for pattern in patterns:
                with self.subTest(file=name, pattern=pattern):
                    self.assertIsNone(re.search(pattern, text))


if __name__ == '__main__':
    unittest.main()
