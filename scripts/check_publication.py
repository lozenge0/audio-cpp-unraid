#!/usr/bin/env python3
"""Publication checks. Diagnostics never echo matched content.

These checks detect selected data formats, not arbitrary personal information.
Human review and GitHub secret protection remain necessary.
"""
import argparse
import base64
import binascii
from pathlib import Path
import re
import struct
import subprocess
import sys
import xml.etree.ElementTree as ET
import zlib


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_FILES = {
    '.github/dependabot.yml', '.github/workflows/validate.yml',
    '.gitignore', 'CHANGELOG.md', 'LICENSE', 'README.md',
    'CONTRIBUTING.md', 'SECURITY.md',
    'assets/README.md', 'assets/icon.svg', 'assets/icon.png', 'ca_profile.xml',
    'docs/CONFIGURATION.md', 'docs/MAINTAINER.md', 'docs/RELEASE-REVIEW.md',
    'docs/VALIDATION.md',
    'docs/reports/CPU-RETEST-20260912.md', 'docs/reports/FIRST-RUN-FINDINGS.md',
    'docs/reports/RECREATION-TEST.md', 'docs/reports/SHORT-TEXT-INVESTIGATION.md',
    'docs/reports/UI-TEST-PREFLIGHT.md', 'docs/reports/UPDATE-ROLLBACK-TEST.md',
    'docs/reports/USER-IDENTITY-TESTS.md', 'templates/audio-cpp.xml',
    'tests/test_ci.py', 'tests/test_publication.py', 'tests/test_template.py',
    'tests/test_publication_guard.py', 'scripts/check_publication.py',
    '.githooks/pre-commit', '.githooks/pre-push', '.githooks/commit-msg',
}
PATTERNS = {
    'home directory': rb'(?:/(?:Users|home)/[A-Za-z0-9_.-]+|[A-Za-z]:\\Users\\[A-Za-z0-9_.-]+)',
    'private network address': rb'\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b',
    'private IPv6 address': rb'\b(?:fc|fd)[0-9a-fA-F]{2}:[0-9a-fA-F:]+',
    'GPU identifier': rb'GPU-[0-9a-fA-F]{8}-[0-9a-fA-F-]{20,}',
    'private key': rb'-----BEGIN (?:OPENSSH |RSA |EC |DSA |ENCRYPTED )?PRIVATE KEY-----',
    'GitHub token': rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})\b',
    'provider token': rb'\b(?:hf_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9_-]{30,}|xox[baprs]-[A-Za-z0-9-]{20,}|AKIA[0-9A-Z]{16})\b',
    'credential in URL': rb'https?://[^\s/:<>]+:[^\s/@<>]+@',
}
EMAIL = re.compile(rb'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
NOREPLY = re.compile(r'(?:\d+\+)?([A-Za-z0-9-]+(?:\[bot\])?)@users\.noreply\.github\.com')


def git(*args, cwd=ROOT):
    return subprocess.run(['git', *args], cwd=cwd, check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout


def sensitive_markers(data):
    findings = {label for label, pattern in PATTERNS.items() if re.search(pattern, data)}
    for match in EMAIL.findall(data):
        address = match.decode('ascii')
        domain = address.rsplit('@', 1)[1].lower()
        if not (NOREPLY.fullmatch(address) or address == 'noreply@github.com'
                or domain in ('example.com', 'example.org', 'example.net')
                or domain.endswith(('.example', '.invalid', '.test'))):
            findings.add('non-public email address')
    return findings


def scan_content(name, data):
    findings = sensitive_markers(data)
    if name.endswith('.svg'):
        try:
            root = ET.fromstring(data)
            for node in root.iter('{http://c2pa.org/manifest}manifest'):
                decoded = base64.b64decode(''.join((node.text or '').split()), validate=True)
                if not decoded:
                    findings.add('empty SVG provenance')
                findings.update('SVG provenance: ' + label for label in sensitive_markers(decoded))
        except (ET.ParseError, ValueError, binascii.Error):
            findings.add('unreadable SVG provenance')
    elif name.endswith('.png'):
        try:
            if data[:8] != b'\x89PNG\r\n\x1a\n':
                raise ValueError()
            offset, chunks = 8, []
            while offset < len(data):
                size = struct.unpack('>I', data[offset:offset + 4])[0]
                kind = data[offset + 4:offset + 8]
                payload = data[offset + 8:offset + 8 + size]
                crc = struct.unpack('>I', data[offset + 8 + size:offset + 12 + size])[0]
                if kind not in (b'IHDR', b'bKGD', b'IDAT', b'IEND') or zlib.crc32(kind + payload) != crc:
                    raise ValueError()
                chunks.append(kind)
                offset += size + 12
            if offset != len(data) or not chunks or chunks[0] != b'IHDR' or chunks[-1] != b'IEND':
                raise ValueError()
        except (ValueError, struct.error):
            findings.add('unexpected PNG structure or metadata')
    else:
        try:
            data.decode('utf-8')
            if b'\0' in data:
                findings.add('unexpected binary content')
        except UnicodeDecodeError:
            findings.add('unexpected binary content')
    return findings


def public_identity(name, email, role):
    if role == 'committer' and (name, email) == ('GitHub', 'noreply@github.com'):
        return True
    match = NOREPLY.fullmatch(email)
    return bool(match and name == match.group(1))


def check_index(cwd=ROOT):
    errors = []
    for entry in git('ls-files', '--stage', '-z', cwd=cwd).split(b'\0'):
        if not entry:
            continue
        metadata, name = entry.split(b'\t', 1)
        mode, oid, stage = metadata.decode().split()
        name = name.decode('utf-8')
        errors += check_blob(name, mode, oid, cwd)
        if stage != '0':
            errors.append('Unresolved index entry (path withheld).')
    for role in ('author', 'committer'):
        identity = git('var', 'GIT_' + role.upper() + '_IDENT', cwd=cwd).decode()
        match = re.fullmatch(r'(.*?) <([^<>]+)> \d+ [+-]\d{4}\n?', identity)
        if not match or not public_identity(*match.groups(), role):
            errors.append('Configured ' + role + ' must use the public handle and matching GitHub noreply email.')
    return errors


def check_blob(name, mode, oid, cwd):
    if name not in PUBLIC_FILES:
        return ['Unapproved publication path (name withheld).']
    if mode not in ('100644', '100755'):
        return [name + ': symlink/submodule or unsupported file mode.']
    data = git('cat-file', 'blob', oid, cwd=cwd)
    return [name + ': ' + label for label in sorted(scan_content(name, data))]


def check_commits(commits, cwd=ROOT):
    errors, seen = [], set()
    for commit in commits:
        raw = git('show', '-s', '--format=%an%x00%ae%x00%cn%x00%ce%x00%B', commit, cwd=cwd)
        author, author_email, committer, committer_email, message = raw.split(b'\0', 4)
        for role, name, email in (('author', author, author_email), ('committer', committer, committer_email)):
            if not public_identity(name.decode('utf-8'), email.decode('utf-8'), role):
                errors.append(commit[:12] + ': non-public ' + role + ' identity (values withheld).')
        errors += [commit[:12] + ': commit message: ' + label for label in sorted(sensitive_markers(message))]
        for entry in git('ls-tree', '-rz', commit, cwd=cwd).split(b'\0'):
            if not entry:
                continue
            metadata, name = entry.split(b'\t', 1)
            mode, kind, oid = metadata.decode().split()
            key = (name, mode, oid)
            if key in seen:
                continue
            seen.add(key)
            errors += [commit[:12] + ': ' + error for error in check_blob(name.decode('utf-8'), mode, oid, cwd)]
    return errors


class IncompleteHistory(ValueError):
    pass


def resolve_commit(revision, cwd=ROOT):
    return git('rev-parse', '--verify', '--end-of-options', revision + '^{commit}', cwd=cwd).decode().strip()


def commits_between(base, tip, cwd=ROOT, published=()):
    if git('rev-parse', '--is-shallow-repository', cwd=cwd).strip() != b'false':
        raise IncompleteHistory('History checks require a complete clone; fetch the full history first.')
    # Resolve user/event values as revisions before handing them to rev-list.
    tip = resolve_commit(tip, cwd)
    args = [tip]
    if base and set(base) != {'0'}:
        base = resolve_commit(base, cwd)
        args.append('^' + base)
    args.extend('^' + resolve_commit(oid, cwd) for oid in published)
    return git('rev-list', *args, cwd=cwd).decode().splitlines()


def remote_commit_tips(remote, cwd=ROOT):
    # Query the actual push destination; stale local tracking refs are not proof
    # that a commit is already published there. Unknown tips exclude nothing.
    tips = set()
    for line in git('ls-remote', '--heads', '--', remote, cwd=cwd).splitlines():
        oid, _ = line.decode().split('\t', 1)
        try:
            tips.add(resolve_commit(oid, cwd))
        except subprocess.CalledProcessError:
            continue
    return tips


def check_push(lines, cwd=ROOT, remote=None):
    commits, errors = set(), []
    published = None
    for line in lines:
        local_ref, local_oid, remote_ref, remote_oid = line.split()
        if set(local_oid) == {'0'}:
            continue  # Deleting a ref publishes no new objects.
        if published is None:
            published = remote_commit_tips(remote, cwd) if remote else ()
        # Scan tagger identity and message too, including nested annotated tags.
        target = local_oid
        while git('cat-file', '-t', target, cwd=cwd).strip() == b'tag':
            raw = git('cat-file', 'tag', target, cwd=cwd)
            headers, _, message = raw.partition(b'\n\n')
            tagger = re.search(rb'^tagger (.*?) <([^<>]+)> \d+ [+-]\d{4}$', headers, re.MULTILINE)
            if not tagger or not public_identity(*(value.decode() for value in tagger.groups()), 'tagger'):
                errors.append('Tag has a non-public tagger identity (values withheld).')
            errors += ['Tag: ' + label for label in sorted(sensitive_markers(raw))]
            target = headers.splitlines()[0].removeprefix(b'object ').decode()
        if git('cat-file', '-t', target, cwd=cwd).strip() != b'commit':
            errors.append('Only commits and tags referring to commits may be published.')
            continue
        commits.update(commits_between(remote_oid, local_oid, cwd, published))
    return errors + check_commits(sorted(commits), cwd)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--staged', action='store_true')
    group.add_argument('--pre-push', action='store_true')
    group.add_argument('--message', type=Path)
    group.add_argument('--since', help='Check commits after this base through --tip; empty means full history')
    group.add_argument('--commit', help='Check one commit and its complete tree, without auditing ancestors')
    parser.add_argument('--tip', default='HEAD', help='History tip for --since (default: HEAD)')
    parser.add_argument('--remote', help='Actual push destination supplied by the pre-push hook')
    args = parser.parse_args()
    try:
        if args.staged:
            errors = check_index()
        elif args.pre_push:
            errors = check_push(sys.stdin, remote=args.remote)
        elif args.message:
            errors = ['Commit message: ' + label for label in sorted(sensitive_markers(args.message.read_bytes()))]
        elif args.commit:
            errors = check_commits([resolve_commit(args.commit)])
        else:
            errors = check_commits(commits_between(args.since, args.tip))
    except IncompleteHistory as error:
        errors = [str(error)]
    except (subprocess.CalledProcessError, OSError, ValueError, UnicodeError):
        # Git errors can include local paths, identities or credentials in URLs.
        errors = ['Publication check could not complete; no sensitive diagnostics printed.']
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        print('Publication blocked. Review locally; do not post raw diagnostics or bypass the check.', file=sys.stderr)
    return bool(errors)


if __name__ == '__main__':
    sys.exit(main())
