# GitHub preparation and publication

The intended destination is `lozenge0/audio-cpp-unraid`, with default branch
`main` and GitHub Issues for support. The owner wants to review the draft on
GitHub. Publishing that draft is separate from approving a beta release or
submitting to Community Apps. The owner explicitly approved standalone Git
initialization and public draft creation/push on 2026-09-12. This is not approval
for a release tag or CA submission. See RELEASE-REVIEW.md for completed operations.

## Clean standalone Git history

The original candidate was prepared inside another checkout. Publication uses
a separate sibling directory and a fresh root commit, with no parent Git history.
For any future restaging, verify the Git root before staging or changing remotes.

Approved initialization procedure:

1. Prefer a new standalone directory outside the upstream checkout. Copy only
   files in the [reviewed inventory](RELEASE-REVIEW.md#exact-proposed-file-list),
   including `.github` and `.gitignore`; do not copy the parent `.git`, history,
   ignored files, original artwork pack or private test artifacts.
2. Initialize that directory with `git init -b main`. Verify
   `git rev-parse --show-toplevel` identifies the new integration directory.
3. Set repository-local author name and email before the first commit. Prefer
   the exact GitHub-provided noreply address from account email settings; do not
   guess its format or inherit a personal email without approval. Do not change
   global Git settings. Review [GitHub's commit-email guidance](https://docs.github.com/en/account-and-profile/how-tos/email-preferences/setting-your-commit-email-address).
4. Run the tests, inspect the file inventory and stage only reviewed files. Review
   `git diff --cached --stat` and `git diff --cached` before the initial commit.
   Use a new root commit, not imported upstream history.
5. Verify GitHub authentication as `lozenge0` without printing tokens. Create an
   empty repository at the agreed destination and visibility after approval;
   do not overwrite an existing repository or auto-add competing licence/README
   files. Verify the remote before pushing `main`. Do not force-push.

Keep the README and template labelled draft during GitHub review. Once actually
published, update the local-only status statements and the status test in
`tests/test_template.py` to reflect reality, without claiming CA acceptance.
No integration release tag or CA submission is part of this initial push.

## CI and repository settings

The prepared workflow runs stdlib Python tests on pushes to `main`, pull requests
and manual dispatch. It uses GitHub-hosted Ubuntu, a read-only repository token,
commit-pinned official actions and no persisted checkout credentials. There are
no application builds, deployments, artifact uploads, scheduled server tasks,
custom secrets or access to Unraid. GitHub provides the ordinary workflow token;
do not add an Unraid SSH key or API token to repository secrets.

Dependabot proposes weekly GitHub Actions dependency updates. It does not track
audio.cpp releases, publish images or merge its own pull requests. Container
updates remain driven by the official upstream tags and each user's Unraid
updater. See [GitHub's workflow security guidance](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions).

After creation, verify rather than assume these settings:

- Default branch `main`; Issues enabled; Actions enabled with read-only default
  token permissions and no permission for Actions to create/approve pull requests.
- Dependabot updates enabled and no auto-merge configured. Review action-pin PRs.
- Require approval for workflows from outside contributors according to the
  repository's Actions settings; never use a self-hosted Unraid runner for PRs.
- Enable private vulnerability reporting and verify the reporting option. See
  [GitHub's setup guidance](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/configure-for-a-repository).
- Verify the first CI run on GitHub; local tests do not establish hosted success.
  Then protect `main` with the observed validation status check and block force
  pushes/deletion where available. A single maintainer need not require an
  impossible approval of their own PR; outside contributions should be reviewed.
- Verify README, Issues, template, profile and raw icon URLs. Check the icon in
  the real CA/Unraid UI as well as local previews. Enable available secret alerts
  and push protection as defense in depth, not a replacement for file review.

The workflow tests design invariants and publication hygiene, not the full CA
schema, container inference, GPU compatibility or live external links.

## Later Community Apps release

Complete or explicitly narrow the remaining [release gates](RELEASE-REVIEW.md),
including actual branch-selection/installation checks, tested image disclosure,
and the relevant lifecycle/configuration tests. Run CA Validate/Scan against the
public repository, resolve findings, obtain owner approval of the reviewed files
and test results, and obtain explicit CA submission approval. Draft repository
publication is not an announcement that these checks passed.
