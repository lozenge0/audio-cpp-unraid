# Release review — GitHub review draft

Updated 2026-09-12. Target: **audio.cpp for Unraid v0.1.0**. Public GitHub draft
publication is approved and being prepared; no beta release or CA submission is
approved. This is the current tracker; dated test reports preserve what was known
during each experiment.

## Proposed repository

- Owner/repository: `lozenge0/audio-cpp-unraid`; default branch: `main`.
- Support: repository GitHub Issues. Public links are configured, not verified live.
- Contents: Unraid template/profile, community artwork, documentation and local
  maintainer tests and CI only. No application code, custom image, runtime wrapper,
  preset model/configuration, personal voice or image-publishing workflow.
- Updates: users follow official moving tags. Passing tests against pinned
  digests does not validate every future image published to those tags.
- Scope: CPU, CUDA 12 and CUDA 13. Runtime evidence is one Unraid 7.3.2 host,
  Ryzen 7 3700X / RTX 3060 12 GB, using Pocket TTS GGUF Q8.
- Licence: owner approved root MIT for integration files and CC0 1.0 for the icon
  on 2026-09-12. The artwork dedication applies only to rights the owner holds;
  see [artwork terms](../assets/README.md). Subsequent GitHub draft publication is
  approved; beta release and CA submission are not.

## Completed evidence

| Area | Supported conclusion | Evidence |
| --- | --- | --- |
| Template | Three complete configurations; upstream-only launch and native identity controls | `tests/test_template.py` |
| Fresh storage | Native downloads work as 99:100 without ownership-changing helpers | [Identity tests](USER-IDENTITY-TESTS.md) |
| Private CA install | Owner installed pre-expanded CPU/CUDA 12/CUDA 13 entries; not the public selector | [UI evidence](VALIDATION.md) |
| CPU regression | Fixed revision `5bea9c7` passes short/long offline, Studio, streaming and restart tests; owner playback confirmed | [CPU retest](CPU-RETEST-20260912.md) |
| CUDA inference | Both variants initialized/computed with CUDA and passed API/Studio tests | [Validation](VALIDATION.md) |
| Restart/model reuse | Files persist; clients explicitly re-register models when required | [Identity tests](USER-IDENTITY-TESTS.md) |
| Same-image recreation | Controlled CUDA 13 recreation preserves settings and model data | [Recreation](RECREATION-TEST.md) |
| Update/rollback | Controlled CUDA 13 upgrade and restoration of retained old container passed; not the full DockerMan/scheduler path | [Update/rollback](UPDATE-ROLLBACK-TEST.md) |

The old CPU image's `hello` crash remains a historical failure. The owner confirmed
the fixed test was "working well" after automated checks; this is listening
confirmation for their sample, not every saved WAV.

## Remaining gates and decisions

Before publishing any repository contents:

- [x] Owner approves the root integration licence (MIT, 2026-09-12).
- [x] Owner approves icon reuse terms (CC0 1.0, 2026-09-12).
- [x] Owner chooses to review the draft on GitHub before beta approval; final beta
  file approval happens after that review.
- [x] Review preserved artwork metadata and render locally at 32/48/180 px on
  white/dark backgrounds. Metadata remains intact; authenticity is not certified.
- [x] Complete independent template, publication-safety and GitHub/CI design
  reviews on September 12. These supersede the earlier usage-limited attempt.
  Findings and follow-up verification are recorded below.
- [x] Owner explicitly approves clean standalone initialization and public
  repository creation/push on September 12. No surrounding checkout/history.
- [ ] Verify the initial public push, hosted CI and repository settings.

Before calling v0.1.0 a Community Apps beta ready for submission:

- [ ] Owner reviews files on GitHub and approves final beta contents/test results.
- [ ] Validate documented optional JSON under UID 99:100, stable model IDs across
  restart and CLI precedence, or clearly defer that recipe.
- [ ] Check the full single-container DockerMan update path and variant-switch
  instructions. Controlled Engine recreation/rollback is narrower evidence.
- [ ] Review scheduled updates safely or explicitly leave unattended updates
  unvalidated. Never invoke a host-wide updater to test one container.
- [ ] Verify GitHub Issues and README/template/raw icon links after approved publication.
- [ ] Validate public CA branch selection and installation fields using a supported
  preview/feed workflow; private pre-expanded entries cannot prove this.
- [ ] Run CA Validate/Scan, resolve findings and obtain explicit submission approval.
  Acceptance is the CA reviewers' decision.
- [ ] Recheck moving tags before release; update the tested-image record or disclose
  newer untested images. Do not label a moving tag permanently verified.

Failure/retry recovery, optional residency/resource controls, other models, GPUs
and Unraid versions are not covered exhaustively. Test or narrow relevant claims;
do not mark the entire acceptance protocol complete from one model installation.

Vulkan is a future scope decision, not an upstream-image availability blocker:
the [reviewed upstream workflow](https://github.com/0xShug0/audio.cpp/blob/5bea9c726881f6a7ce3e9adf18c060b5a6a8eb8e/.github/workflows/docker.yml)
includes it. No Vulkan branch, AMD/Intel compatibility claim or new deployment is
authorized here. CPU/CUDA can remain the first release scope.

The sequence follows [CA submission guidance](https://ca.unraid.net/submit/help):
public active repository, OSI-approved root licence, profile/template metadata,
then Validate/Scan. Local preparation does not authorize these external steps.

## Exact proposed file list

Only these relative paths belong in the future repository after approval.
Local publication tests enforce this list, excluding ignored Python caches.

```text
.github/dependabot.yml
.github/workflows/validate.yml
.gitignore
CHANGELOG.md
CONTRIBUTING.md
LICENSE
README.md
SECURITY.md
assets/README.md
assets/icon.svg
ca_profile.xml
docs/CPU-RETEST-20260912.md
docs/FIRST-RUN-FINDINGS.md
docs/PLAN.md
docs/PUBLISHING.md
docs/RECREATION-TEST.md
docs/RELEASE-REVIEW.md
docs/SHORT-TEXT-INVESTIGATION.md
docs/UI-TEST-PREFLIGHT.md
docs/UPDATE-ROLLBACK-TEST.md
docs/USER-IDENTITY-TESTS.md
docs/VALIDATION.md
templates/audio-cpp.xml
tests/test_ci.py
tests/test_publication.py
tests/test_template.py
```

Never include the parent checkout/history, `speak.sh`, `.devops/unraid`, SSH/API
credentials, test harnesses, raw Docker inspections, WAVs/screenshots, downloaded
models, personal configuration or original icon pack. Reports here contain selected
technical evidence; raw artifacts stay outside this folder.

## Local review procedure

Run `python3 -m unittest discover -s tests -v` from this directory. Checks cover
structure, explicit file inventory, relative documentation links and selected
accidental-data patterns. They are not a complete secret scanner, legal clearance,
CA validation or proof of current upstream compatibility. The same tests are
prepared for read-only GitHub Actions CI; hosted execution is not verified yet.
No image build, custom CI credentials or server access is required.

The September 12 licence update passed the then-current 21 checks. The subsequent
three independent reviews found no template launch or publication-safety blocker
for a clearly labelled GitHub draft. Corrections remove a host-specific GPU ID
prefix from a negative test fixture, label optional JSON guidance unvalidated,
distinguish the CPU image/config ID from pullable digests, and separate GitHub
review publication from CA release. The inventory guard now checks symlinks before
exclusions and permits only root Git metadata and recognized test bytecode caches.

Preparation adds read-only, commit-pinned CI, Dependabot action updates and
contribution/security/publishing guidance. The exact inventory is now 26 files;
the suite includes 16 template, five publication and four CI policy checks.
These CI checks inspect policy text, not the complete GitHub workflow schema.
Final local verification: all **25 tests passed**, both YAML files parsed locally,
and all three reviewers rechecked the final changes with no blocking findings
for GitHub draft publication. Each independently reran the 25-test suite. Hosted
CI execution, actual CA rendering and repository settings remain unverified.
See [publishing steps](PUBLISHING.md) for author-email privacy, clean Git history,
repository settings and first hosted-CI verification. The standard root MIT text
and original SVG remain unchanged. The prepublication review involved no Git
initialization, commits, server operations, GitHub writes or CA submissions.
The owner subsequently approved the separate GitHub publication step above.
