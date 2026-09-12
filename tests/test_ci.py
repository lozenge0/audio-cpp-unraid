"""Offline CI policy guardrails; not a complete GitHub workflow/YAML validator."""
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class CIPolicyTests(unittest.TestCase):
    def setUp(self):
        self.workflow = (ROOT / '.github/workflows/validate.yml').read_text()

    def test_official_actions_are_commit_pinned(self):
        actions = re.findall(r'^\s+uses: (\S+)', self.workflow, re.MULTILINE)
        self.assertEqual(len(actions), 2)
        self.assertEqual({value.split('@')[0] for value in actions},
                         {'actions/checkout', 'actions/setup-python'})
        for action in actions:
            self.assertRegex(action, r'^actions/[a-z-]+@[0-9a-f]{40}$')

    def test_read_only_hosted_validation(self):
        for required in (
            'permissions:\n  contents: read\n',
            'persist-credentials: false', 'runs-on: ubuntu-24.04',
            'timeout-minutes: 5', 'python -m unittest discover -s tests -v',
        ):
            self.assertIn(required, self.workflow)
        for forbidden in ('pull_request_target', 'self-hosted', 'secrets.',
                          'write-all', ': write', 'docker ', 'ssh ',
                          'upload-artifact', 'workflow_run', 'schedule:'):
            self.assertNotIn(forbidden, self.workflow)
        self.assertEqual(len(re.findall(r'^\s+run:', self.workflow, re.MULTILINE)), 1)

    def test_expected_triggers(self):
        self.assertIn('on:\n  push:\n    branches: [main]\n  pull_request:\n'
                      '  workflow_dispatch:\n', self.workflow)

    def test_dependabot_updates_actions_only(self):
        config = (ROOT / '.github/dependabot.yml').read_text()
        self.assertIn('version: 2', config)
        self.assertEqual(re.findall(r'package-ecosystem: (\S+)', config),
                         ['github-actions'])
        self.assertIn('directory: /', config)
        self.assertIn('interval: weekly', config)
        self.assertIn('open-pull-requests-limit: 5', config)


if __name__ == '__main__':
    unittest.main()
