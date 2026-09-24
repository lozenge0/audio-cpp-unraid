"""Exercise publication boundaries with synthetic data in disposable Git repos."""
import base64
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts.check_publication import (
    ROOT, IncompleteHistory, check_commits, check_index, check_push, commits_between,
    public_identity, scan_content, sensitive_markers,
)


class ContentTests(unittest.TestCase):
    def test_sensitive_formats_and_no_test_file_exemption(self):
        samples = [
            b'10.' + b'20.30.40', b'172.' + b'20.30.40', b'192.' + b'168.2.3',
            b'/Users/' + b'synthetic/input.wav', b'/home/' + b'synthetic/config',
            b'C:\\Users\\' + b'synthetic\\input.wav',
            b'ghp_' + b'x' * 36, b'hf_' + b'x' * 36,
            b'-----BEGIN ' + b'PRIVATE KEY-----',
            b'person@' + b'private-mail.invalid-domain.com',
            b'https://' + b'person:secret@example.com',
        ]
        for sample in samples:
            with self.subTest(kind=samples.index(sample)):
                self.assertTrue(scan_content('tests/test_template.py', sample))

    def test_public_examples_and_hashes_are_allowed(self):
        self.assertFalse(sensitive_markers(
            b'contact@example.com reviewer@users.noreply.github.com sha256:' + b'a' * 64))

    def test_svg_provenance_is_decoded(self):
        payload = base64.b64encode(b'ghp_' + b'x' * 36)
        svg = b'<svg xmlns:c="http://c2pa.org/manifest"><c:manifest>' + payload + b'</c:manifest></svg>'
        self.assertIn('SVG provenance: GitHub token', scan_content('assets/icon.svg', svg))
        self.assertIn('unreadable SVG provenance', scan_content('assets/icon.svg', b'<svg>'))

    def test_png_extra_metadata_and_binary_content_are_rejected(self):
        image = (ROOT / 'assets/icon.png').read_bytes()
        self.assertFalse(scan_content('assets/icon.png', image))
        self.assertTrue(scan_content('assets/icon.png', image + b'private metadata'))
        self.assertTrue(scan_content('README.md', b'\0binary'))

    def test_noreply_email_does_not_hide_author_name(self):
        self.assertTrue(public_identity('reviewer', '123+reviewer@users.noreply.github.com', 'author'))
        self.assertFalse(public_identity('Personal Name', '123+reviewer@users.noreply.github.com', 'author'))
        self.assertTrue(public_identity('GitHub', 'noreply@github.com', 'committer'))
        self.assertFalse(public_identity('GitHub', 'noreply@github.com', 'author'))


class GitBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.repo = Path(self.directory.name)
        # Never inherit the developer's identity, hooks, signing or Git context.
        env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
        env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1',
                   GIT_AUTHOR_NAME='reviewer', GIT_COMMITTER_NAME='reviewer',
                   GIT_AUTHOR_EMAIL='reviewer@users.noreply.github.com',
                   GIT_COMMITTER_EMAIL='reviewer@users.noreply.github.com')
        self.environment = patch.dict(os.environ, env, clear=True)
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.git('init', '-q')
        (self.repo / 'README.md').write_text('Public documentation.\n')
        self.git('add', 'README.md')
        self.git('commit', '-qm', 'Initial public documentation')
        self.base = self.git('rev-parse', 'HEAD').strip()

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.repo, stderr=subprocess.PIPE).decode()

    def commit_text(self, text, message='Update documentation'):
        (self.repo / 'README.md').write_text(text)
        self.git('add', 'README.md')
        self.git('commit', '-qm', message)
        return self.git('rev-parse', 'HEAD').strip()

    def install_hooks(self):
        shutil.copytree(ROOT / '.githooks', self.repo / '.githooks')
        (self.repo / 'scripts').mkdir()
        shutil.copy(ROOT / 'scripts/check_publication.py', self.repo / 'scripts/check_publication.py')
        self.git('config', 'core.hooksPath', '.githooks')

    def make_remote(self, empty=False):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        remote = Path(directory.name) / 'remote.git'
        if empty:
            self.git('init', '--bare', '-q', str(remote))
        else:
            self.git('clone', '--bare', '-q', str(self.repo), str(remote))
        return str(remote)

    def test_shallow_history_fails_full_range_and_push_checks(self):
        self.commit_text('ghp_' + 'x' * 36)
        tip = self.commit_text('Clean latest tree')
        clone = self.repo / 'shallow'
        self.git('clone', '-q', '--depth', '1', self.repo.as_uri(), str(clone))
        self.assertTrue(check_commits(commits_between('', 'HEAD', self.repo), self.repo))
        for base in ('', tip):
            with self.subTest(base=bool(base)), self.assertRaises(IncompleteHistory):
                commits_between(base, 'HEAD', clone)
        zero = '0' * 40
        with self.assertRaises(IncompleteHistory):
            check_push([f'refs/heads/new {tip} refs/heads/new {zero}'], clone)
        self.assertFalse(check_push([f'(delete) {zero} refs/heads/main {tip}'], clone))

    def test_push_uses_destination_history_and_still_checks_new_commits(self):
        self.commit_text('ghp_' + 'x' * 36)
        self.commit_text('Already published clean tree')
        remote = self.make_remote()
        self.install_hooks()
        self.commit_text('Safe new work')
        self.git('push', remote, 'HEAD:refs/heads/new')
        # Simulate intermediate commits made without hooks, then restore hooks.
        self.git('config', 'core.hooksPath', '.unused-hooks')
        self.commit_text('hf_' + 'x' * 36)
        self.commit_text('Clean latest tree')
        self.git('config', 'core.hooksPath', '.githooks')
        blocked = subprocess.run(['git', 'push', remote, 'HEAD:refs/heads/new'],
                                 cwd=self.repo, capture_output=True)
        self.assertNotEqual(blocked.returncode, 0)
        self.assertIn(b'provider token', blocked.stderr)

    def test_empty_destination_does_not_trust_other_remote_or_tracking_refs(self):
        self.commit_text('ghp_' + 'x' * 36)
        tip = self.commit_text('Clean latest tree')
        published_remote = self.make_remote()
        empty_remote = self.make_remote(empty=True)
        self.git('update-ref', 'refs/remotes/origin/main', tip)
        update = [f'refs/heads/new {tip} refs/heads/new {"0" * 40}']
        self.assertFalse(check_push(update, self.repo, published_remote))
        self.assertTrue(check_push(update, self.repo, empty_remote))
        self.assertTrue(check_commits(commits_between('', 'HEAD', self.repo), self.repo))

    def test_unreadable_remote_fails_closed(self):
        update = [f'refs/heads/new {self.base} refs/heads/new {"0" * 40}']
        with self.assertRaises(subprocess.CalledProcessError):
            check_push(update, self.repo, str(self.repo / 'missing-remote'))

    def test_single_commit_check_is_distinct_from_full_history_audit(self):
        self.commit_text('ghp_' + 'x' * 36)
        self.commit_text('Clean latest tree')
        self.install_hooks()
        def run(*args):
            return subprocess.run(['python3', 'scripts/check_publication.py', *args],
                                  cwd=self.repo, capture_output=True)
        self.assertEqual(run('--commit', 'HEAD').returncode, 0)
        self.assertNotEqual(run('--since', '').returncode, 0)
        self.git('config', 'core.hooksPath', '.unused-hooks')
        self.commit_text('hf_' + 'x' * 36)
        self.assertNotEqual(run('--commit', 'HEAD').returncode, 0)

    def test_explicit_history_tip_excludes_synthetic_merge_identity(self):
        tip = self.commit_text('Safe proposed commit')
        with patch.dict(os.environ, {'GIT_AUTHOR_NAME': 'Personal Name'}):
            self.commit_text('Synthetic merged tree')
        self.install_hooks()
        command = ['python3', 'scripts/check_publication.py', '--since', self.base]
        self.assertNotEqual(subprocess.run(command, cwd=self.repo, capture_output=True).returncode, 0)
        self.assertEqual(subprocess.run(command + ['--tip', tip], cwd=self.repo,
                                        capture_output=True).returncode, 0)

    def test_index_is_checked_even_when_working_copy_is_clean(self):
        secret = 'ghp_' + 'x' * 36
        (self.repo / 'README.md').write_text(secret)
        self.git('add', 'README.md')
        (self.repo / 'README.md').write_text('Clean working copy')
        findings = check_index(self.repo)
        self.assertTrue(any('GitHub token' in item for item in findings))
        self.assertNotIn(secret, '\n'.join(findings))

    def test_push_checks_removed_secrets_in_intermediate_commits(self):
        secret = 'ghp_' + 'x' * 36
        self.commit_text(secret)
        tip = self.commit_text('Clean latest tree')
        findings = check_push([f'refs/heads/main {tip} refs/heads/main {self.base}'], self.repo)
        self.assertTrue(any('GitHub token' in item for item in findings))
        self.assertNotIn(secret, '\n'.join(findings))

    def test_new_branch_checks_history_and_deletion_is_allowed(self):
        self.commit_text('ghp_' + 'x' * 36)
        tip = self.commit_text('Clean latest tree')
        zero = '0' * 40
        self.assertTrue(check_push([f'refs/heads/new {tip} refs/heads/new {zero}'], self.repo))
        self.assertFalse(check_push([f'(delete) {zero} refs/heads/main {tip}'], self.repo))

    def test_safe_push_and_public_identity(self):
        tip = self.commit_text('Safe update')
        self.assertFalse(check_push([f'refs/heads/main {tip} refs/heads/main {self.base}'], self.repo))
        with patch.dict(os.environ, {'GIT_AUTHOR_NAME': 'Personal Name'}):
            bad = self.commit_text('Another update')
        findings = check_commits([bad], self.repo)
        self.assertTrue(any('author identity' in item for item in findings))
        self.assertNotIn('Personal Name', '\n'.join(findings))

    def test_unapproved_files_and_symlinks_are_rejected(self):
        (self.repo / 'private.txt').write_text('Local only')
        self.git('add', 'private.txt')
        self.assertIn('Unapproved publication path (name withheld).', check_index(self.repo))
        self.git('reset', '-q', 'HEAD', 'private.txt')
        (self.repo / 'README.md').unlink()
        (self.repo / 'README.md').symlink_to('private.txt')
        self.git('add', 'README.md')
        self.assertTrue(any('symlink' in item for item in check_index(self.repo)))

    def test_tag_metadata_is_checked(self):
        tip = self.commit_text('Safe update')
        secret = 'hf_' + 'x' * 36
        self.git('tag', '-a', 'v-test', '-m', secret)
        tag = self.git('rev-parse', 'v-test').strip()
        findings = check_push([f'refs/tags/v-test {tag} refs/tags/v-test {"0" * 40}'], self.repo)
        self.assertTrue(any('provider token' in item for item in findings))
        self.assertNotIn(secret, '\n'.join(findings))

    def test_actual_hooks_block_commit_and_message(self):
        self.install_hooks()
        (self.repo / 'README.md').write_text('ghp_' + 'x' * 36)
        self.git('add', 'README.md')
        blocked = subprocess.run(['git', 'commit', '-qm', 'Unsafe content'], cwd=self.repo, capture_output=True)
        self.assertNotEqual(blocked.returncode, 0)
        self.assertEqual(self.git('rev-parse', 'HEAD').strip(), self.base)
        (self.repo / 'README.md').write_text('Safe content')
        self.git('add', 'README.md')
        blocked = subprocess.run(['git', 'commit', '-qm', 'ghp_' + 'x' * 36], cwd=self.repo, capture_output=True)
        self.assertNotEqual(blocked.returncode, 0)
        self.git('commit', '-qm', 'Safe content and message')


if __name__ == '__main__':
    unittest.main()
