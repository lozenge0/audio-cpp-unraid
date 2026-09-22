# Maintainer guide

For installation and everyday use, start with the [README](../README.md).
This page holds project scope, fixed decisions, the release process and the
maintainer checks. [The release review](RELEASE-REVIEW.md) is the status
tracker. Dated experiment reports live in `docs/reports/`.

## Status and evidence

The current submission state, completed evidence and remaining gates live in
[the release review](RELEASE-REVIEW.md). Do not repeat that status here.

CPU, CUDA 12 and CUDA 13 passed isolated Pocket TTS testing on one Unraid host.
Native Docker `--user=99:100` resolved the initial model-folder permission
failure. The [September 12 CPU retest](reports/CPU-RETEST-20260912.md) passed
short-text, streaming and restart checks on a fixed official image. Controlled
CUDA 13 recreation, image update and rollback passed within their documented
scope. These are not full Community Apps release acceptance, and portal approval
does not establish runtime compatibility.

## Decisions fixed by the project owner

- Project: audio.cpp for Unraid. Repository: `lozenge0/audio-cpp-unraid`.
  Support: repository GitHub Issues.
- Template: CPU base with CUDA 12 and CUDA 13 branches, all on unmodified
  upstream images and moving upstream tags. No custom image, fork, runtime
  wrapper, personal code or configuration.
- Every variant runs as Docker `--user=99:100`. No ownership-changing helper
  and no `PUID`/`PGID` mapping.
- Standard Unraid controls only, plus optional upstream CLI arguments or a
  user-owned JSON file.
- Licences: MIT for integration files and CC0 1.0 for the icon, approved on
  2026-09-12. The artwork dedication covers only the rights the owner holds.
  The owner confirmed the artwork came from their own prompts with Claude/AI.
- Versions: `v0.1.0` is the first beta release. `v1.0.0` is reserved for a
  validated stable integration. Integration versions do not describe the
  upstream audio.cpp version inside the container.
- Vulkan branch for AMD and Intel GPUs added on 2026-09-13 at the owner's
  decision, before any hardware test. The first report comes from a volunteer
  installation through the public listing. The branch says so in its
  description and `Requires` text until a dated report exists. NVIDIA on
  Vulkan is out of scope because the image has no NVIDIA driver.

## Scope and layout

This is a standalone integration repository with its own clean Git history.
It was prepared separately from the upstream audio.cpp source. No upstream
checkout or history belongs here. Do not build an application image from this
repository. Nothing here changes an existing personal installation.

- `templates/audio-cpp.xml`: one app with CPU base, two CUDA branches and a
  Vulkan branch.
- `ca_profile.xml`: Community Apps repository metadata.
- `assets/`: community integration icon and provenance/licensing notes.
- `docs/CONFIGURATION.md`: detailed deployment and tuning notes.
- `docs/RELEASE-REVIEW.md`: current status, evidence and remaining gates.
- `docs/VALIDATION.md`: acceptance checklist and evidence requirements.
- `docs/reports/`: dated experiment reports. They record what was known at
  the time. Label privacy amendments; preserve original test conclusions.
- `tests/`: maintainer-only structural checks, never shipped into the container.
- `scripts/check_publication.py` and `.githooks/`: publication checks.
- `.github/`: read-only CI checks and Dependabot updates for the CI actions only.

The project is called **audio.cpp for Unraid**. The template and container name
is `audio-cpp`. This integration does not imply endorsement by the audio.cpp
maintainers or Unraid.

## Maintainer checks

Run from the repository root, with Python 3.9 or later:

```sh
python3 -m unittest discover -s tests -v
```

These checks validate local structural invariants, not the CA parser, live
registry availability, hardware, browser workflows or installation success.
The publication test uses the exact inventory in `scripts/check_publication.py`.
If you add a file, review its publication safety first, then add it to that list.

Follow the identity and hook setup in [Contributing](../CONTRIBUTING.md) for each
checkout. The pre-commit hook inspects the index, not unstaged working files.
The pre-push hook inspects the commits actually being sent, including intermediate
trees and commit/tag identities. It fails closed when history cannot be read.
History checks reject shallow clones. Fetch the full history before retrying.
The push hook queries the actual push destination and excludes history reachable
from its advertised branch tips that can be resolved locally. Missing local
objects exclude nothing; stale remote-tracking refs are never used as evidence
of publication. A destination query failure blocks the push. Other checks run
offline.
Local tool state is ignored, and ignored files are still rejected if force-added.

For a read-only audit of all history reachable from HEAD, run:

```sh
python3 scripts/check_publication.py --since ''
```

Use `--since BASE_COMMIT` to inspect only subsequent commits, optionally ending
at `--tip COMMIT` instead of HEAD. Pull-request CI audits the actual proposed
commits from base to head, excluding GitHub's synthetic test-merge identity;
structural tests still run on the merged tree. Push CI uses the pre-push branch
tip as its base. Manual dispatch checks the selected commit
and its full tree with `--commit HEAD`; it is not a full-history audit.
Historical privacy findings can therefore fail a full audit even after current
files are sanitized. Do not suppress them to claim the history has been cleaned.
Existing published history has identity, message-email and historical-inventory
findings under the new policy. Excluding already-published ancestors from a push
check does not remediate those findings or certify that history as clean.
GitHub browser merges also need a public author name; local configuration cannot
control that separate identity.

Checks cover selected credential formats, private addresses, home paths and
email addresses across all approved files, including tests. SVG C2PA provenance
is decoded and scanned; PNG metadata is restricted. This is not exhaustive
secret detection or proof of anonymity. Review prose and other encoded content
manually, and retain GitHub secret scanning and push protection.

GitHub Actions runs the tests and commit publication checks on pushes, pull
requests and manual dispatch. The workflow uses GitHub-hosted Ubuntu, a read-only repository token,
commit-pinned official actions and no persisted checkout credentials. There are
no application builds, deployments, artifact uploads, scheduled server tasks,
custom secrets or access to Unraid. Do not add an Unraid SSH key or API token to
repository secrets. Dependabot proposes weekly updates for the CI actions only.
It does not track audio.cpp releases or merge its own pull requests.

Keep these repository settings:

- Default branch `main` is protected by the validation status check. Force
  pushes and deletion are blocked.
- Issues are enabled. Auto-merge is disabled.
- The Actions token is read-only, Actions cannot approve pull requests, and
  workflows from outside contributors need approval.
- Private vulnerability reporting, secret scanning and push protection are on.

See [contribution guidance](../CONTRIBUTING.md) and
[security reporting](../SECURITY.md).

## Release process

1. Run the maintainer checks. For a template change, also run CA Validate/Scan
   against the public repository and resolve findings.
2. If a change affects installed users, add a dated entry to the `Changes`
   field in `templates/audio-cpp.xml`. Community Apps shows that field as the app
   changelog. Docker Manager does not refresh installed templates, so the entry
   must say what an existing user needs to change by hand. Mirror the entry in
   `CHANGELOG.md`.
3. Update the [release review](RELEASE-REVIEW.md) status section and, for
   runtime changes, the [validation checklist](VALIDATION.md). Record runtime
   tests in a dated report under `docs/reports/`. CI has no Unraid server or GPU.
4. Open a pull request and merge it after CI passes.
5. Once the app is visible in the public catalog and the open release gates are
   complete or explicitly deferred, tag `v0.1.0` and create a GitHub release
   from the changelog.

Never publish the surrounding audio.cpp checkout. If the repository is ever
restaged, start from a new directory and make sure that
`git rev-parse --show-toplevel` points at it. Copy only the files in the
publication list. Use a public handle and matching GitHub noreply commit identity, with a fresh root
commit. Never force-push.

Removing data from current files or changing the local identity does not erase
published commits. History remediation requires a separately reviewed rewrite
in an isolated copy, verification of all affected refs, and explicit approval
before any protected-branch exception or remote replacement. Rewritten commits
lose their old signatures and IDs. Forks, existing clones and cached pull-request
views can retain earlier objects; follow
[GitHub's sensitive-data removal guidance](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).

## Ongoing maintenance

Upstream images update independently. Monitor changes to launch arguments,
permissions, storage, driver requirements and security. If one of them
changes, update the template and docs. Changes that affect existing
installations need explicit migration instructions in the README and in the
`Changes` field. No remote access to other users' servers is required.
Release-only image tags are a separate upstream request.

Testing on the owner's server follows fixed rules. Use a separate container
name, an unused port and a fresh appdata directory. Never replace the personal
container. Never run a host-wide updater to test one container. Make sure that
free disk space is enough before you pull more CUDA images.

## Primary references

- [Upstream Docker guide](https://github.com/0xShug0/audio.cpp/blob/main/docs/docker.md)
- [Upstream Docker publishing workflow](https://github.com/0xShug0/audio.cpp/blob/main/.github/workflows/docker.yml)
- [Upstream server guide](https://github.com/0xShug0/audio.cpp/blob/main/app/server/README.md)
- [CA starter repository](https://github.com/unraid/unraid-community-apps-starter)
- [CA submission requirements](https://ca.unraid.net/submit/help)
- [CA XML fields](https://ca.unraid.net/submit/help/xml-field-reference)
- [Unraid container settings](https://docs.unraid.net/unraid-os/using-unraid-to/run-docker-containers/managing-and-customizing-containers/)
- [NVIDIA container GPU selection](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/docker-specialized.html)
- [CUDA 13 compatibility changes](https://docs.nvidia.com/cuda/archive/13.0.0/cuda-toolkit-release-notes/index.html)
- [GitHub workflow security guidance](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions)

## Licensing

The [MIT licence](../LICENSE) applies to this integration's templates,
documentation and tests, not to upstream software, third-party dependencies or
model weights. The icon is separately dedicated under CC0 1.0 Universal, to the
extent the owner holds applicable rights. See
[artwork provenance and terms](../assets/README.md).
