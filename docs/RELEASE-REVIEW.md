# Release review — beta integration

Updated 2026-09-13 (Europe/London). Target: **audio.cpp for Unraid v0.1.0**.
The public repository is published. The owner reports completing CA submission
and receiving automatic approval; catalog visibility and public installation are
not yet verified. No versioned integration release has been created. This is the
current tracker; dated test reports preserve what was known during each experiment.

## Proposed repository

- Owner/repository: `lozenge0/audio-cpp-unraid`; default branch: `main`.
- Support: repository GitHub Issues. Repository/Issues/advisories pages returned
  HTTP 200; public README/template/profile/icon bytes match the local files.
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
  approved. The owner subsequently completed CA submission and reported auto-approval.

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
- [x] Verify the initial public push, hosted CI and repository security settings
  listed in the publication record below.

Post-submission verification and remaining deployment gates:

- [x] Owner reviewed the GitHub files, completed submission and reported auto-approval.
- [ ] Independently verify catalog visibility and the accepted template contents.
- [ ] Validate documented optional JSON under UID 99:100, stable model IDs across
  restart and CLI precedence, or clearly defer that recipe.
- [ ] Check the full single-container DockerMan update path and variant-switch
  instructions. Controlled Engine recreation/rollback is narrower evidence.
- [ ] Review scheduled updates safely or explicitly leave unattended updates
  unvalidated. Never invoke a host-wide updater to test one container.
- [x] Verify GitHub Issues and README/template/raw icon links after approved publication.
- [ ] Validate public CA branch selection and installation fields using a supported
  preview/feed workflow; private pre-expanded entries cannot prove this.
- [ ] Review portal Validate/Scan results and rerun after meaningful XML changes.
  Owner-reported auto-approval does not prove every runtime acceptance check passed.
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
used by read-only GitHub Actions CI; the first hosted run passed all 25 tests.
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
for GitHub draft publication. Each independently reran the 25-test suite.
Actual CA rendering remains unverified; hosted CI and repository verification
are recorded below.
See [publishing steps](PUBLISHING.md) for author-email privacy, clean Git history,
repository settings and first hosted-CI verification. The standard root MIT text
and original SVG remain unchanged. The prepublication review involved no Git
initialization, commits, server operations, GitHub writes or CA submissions.
The owner subsequently approved the separate GitHub publication step above.

## GitHub publication record — September 13 (Europe/London)

- Public repository: [lozenge0/audio-cpp-unraid](https://github.com/lozenge0/audio-cpp-unraid),
  default branch `main`, Issues enabled. No release/tag or CA submission created.
- Fresh signed root commit: `d40ecdfe65dc24509d144264c289ac51e06223c2`, containing
  exactly the 26 reviewed files, no parent history. Author and committer use the
  owner's approved GitHub noreply identity; GitHub reports the signature verified.
- [First hosted validation](https://github.com/lozenge0/audio-cpp-unraid/actions/runs/34725657862)
  passed all 25 tests. The first Dependabot Actions update check also completed
  successfully. No custom CI secrets, image builds or server access were added.
- Workflow token default is read-only; Actions cannot approve PRs. Fork workflows
  require approval for all external contributors. Private vulnerability reporting,
  secret scanning and secret push protection are enabled; auto-merge is disabled.
- Public repository, Issues and advisories links returned HTTP 200. Downloaded
  README/template/profile/icon hashes match local files; the original icon is
  unchanged. This does not validate the CA UI or public branch picker.
- The extra publication-settings subagent hit a usage limit; the earlier three
  independent file/CI reviews remain valid. Remaining settings were verified
  directly against GitHub documentation and API responses, not claimed as a new
  successful independent review.

The first commit and CI timestamps are September 12 in UTC (after midnight
September 13 locally). Dated runtime evidence has not been rerun for publication.
No Unraid operations were performed.

## Category and submission status update

After publication, the owner reported completing CA submission with automatic
approval, but could not yet find the app in the catalog. The template now requests
`AI Tools:`; both category identifiers are present in the public
[CA category list](https://github.com/Squidly271/AppFeed/blob/master/categoryList.json).
The base and both CUDA branches inherit these categories and retain `Beta=true`.
Removed obsolete pre-submission wording without marking public installation,
DockerMan lifecycle tests or other pending runtime checks complete. No container
image, arguments, mounts, ports, user identity or GPU options were changed.

The original 25 checks remain, with one additional category/beta regression check.
Catalog processing time and the reason for delayed visibility have not been
established. No duplicate submission or Unraid changes were made for this update.
