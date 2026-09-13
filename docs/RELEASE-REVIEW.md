# Release review

## Status

Updated 2026-09-13 (Europe/London). Target: **audio.cpp for Unraid v0.1.0**.
This section is the single source for project status. Other documents link
here instead of repeating it.

- The public repository `lozenge0/audio-cpp-unraid` is live with CI.
- The owner completed the Community Apps submission and reported automatic
  approval. Catalog visibility and installation through the public listing are
  not yet verified.
- The app is visible in the public catalog: the Community Apps feed built on
  2026-09-13 lists `audio-cpp` with both CUDA branches expanded.
- No versioned integration release or tag exists.
- Beta status applies to every variant. Runtime evidence covers one host.
- The AMD / Intel Vulkan branch was published on 2026-09-13 without a hardware
  test, at the owner's decision. A volunteer tester with an AMD or Intel GPU
  installs it from the public listing and reports whether the GPU is used.

Dated test reports in this folder preserve what was known during each experiment.

## Proposed repository

- Owner/repository: `lozenge0/audio-cpp-unraid`. Default branch: `main`.
- Support: repository GitHub Issues.
- Contents: Unraid template/profile, community artwork, documentation and local
  maintainer tests and CI only. No application code, custom image, runtime wrapper,
  preset model/configuration, personal voice or image-publishing workflow.
- Updates: users follow official moving tags. Passing tests against pinned
  digests does not validate every future image published to those tags.
- Scope: CPU, CUDA 12, CUDA 13 and Vulkan (AMD/Intel). Runtime evidence is one
  Unraid 7.3.2 host, Ryzen 7 3700X / RTX 3060 12 GB, using Pocket TTS GGUF Q8.
  The Vulkan variant has no runtime evidence yet.
- Categories: the template requests `AI` and `Tools:`. Both identifiers are in
  the public [CA category list](https://github.com/Squidly271/AppFeed/blob/master/categoryList.json).
- Licence: owner approved root MIT for integration files and CC0 1.0 for the icon
  on 2026-09-12. The artwork dedication applies only to rights the owner holds.
  See [artwork terms](../assets/README.md).

## Completed evidence

| Area | Supported conclusion | Evidence |
| --- | --- | --- |
| Template | Four complete configurations. Upstream-only launch and native identity controls | `tests/test_template.py` |
| Fresh storage | Native downloads work as 99:100 without ownership-changing helpers | [Identity tests](reports/USER-IDENTITY-TESTS.md) |
| Private CA install | Owner installed pre-expanded CPU/CUDA 12/CUDA 13 entries, not the public selector | [UI evidence](VALIDATION.md) |
| CPU regression | Fixed revision `5bea9c7` passes short/long offline, Studio, streaming and restart tests. Owner playback confirmed | [CPU retest](reports/CPU-RETEST-20260912.md) |
| CUDA inference | Both variants initialized/computed with CUDA and passed API/Studio tests | [Validation](VALIDATION.md) |
| Restart/model reuse | Files persist. Some clients must re-register models after a restart | [Identity tests](reports/USER-IDENTITY-TESTS.md) |
| Same-image recreation | Controlled CUDA 13 recreation preserves settings and model data | [Recreation](reports/RECREATION-TEST.md) |
| Update/rollback | Controlled CUDA 13 upgrade and restoration of retained old container passed. Not the full DockerMan/scheduler path | [Update/rollback](reports/UPDATE-ROLLBACK-TEST.md) |

The old CPU image's `hello` crash remains a historical failure. The owner confirmed
the fixed test was "working well" after automated checks. This is listening
confirmation for their sample, not every saved WAV.

## Remaining gates and decisions

Completed before publication:

- [x] Owner approved the root integration licence (MIT, 2026-09-12).
- [x] Owner approved icon reuse terms (CC0 1.0, 2026-09-12).
- [x] Owner reviewed the draft on GitHub before beta approval.
- [x] Artwork metadata preserved. Icon rendered locally at 32/48/180 px on
  white and dark backgrounds. Authenticity is not certified.
- [x] Template, publication-safety and CI reviews completed on September 12.
- [x] Clean standalone repository created and pushed on September 12 with no
  surrounding checkout or history.
- [x] Initial public push, hosted CI and repository security settings verified.
- [x] Owner completed the CA submission and reported automatic approval.
- [x] GitHub Issues and README/template/raw icon links verified after publication.

Still open:

- [ ] Independently verify catalog visibility and the accepted template contents.
- [ ] Validate documented optional JSON under UID 99:100, stable model IDs across
  restart and CLI precedence, or clearly defer that recipe.
- [ ] Check the full single-container DockerMan update path and variant-switch
  instructions. Controlled Engine recreation/rollback is narrower evidence.
- [ ] Review scheduled updates safely or explicitly leave unattended updates
  unvalidated. Never invoke a host-wide updater to test one container.
- [ ] Validate public CA branch selection and installation fields using a supported
  preview/feed workflow. Private pre-expanded entries cannot prove this.
- [ ] Review portal Validate/Scan results and rerun after meaningful XML changes.
  Owner-reported auto-approval does not prove every runtime acceptance check passed.
- [ ] Recheck moving tags before release. Update the tested-image record or disclose
  newer untested images. Do not label a moving tag permanently verified.
- [ ] Record the first Vulkan hardware report under `docs/reports/` (GPU model,
  Unraid version, `--list-devices` output, `/health`, generation result). Then
  remove the "not yet hardware-tested" wording from the branch, or narrow the
  claim if the test fails.
- [ ] Tag `v0.1.0` once the remaining gates are complete or explicitly deferred.

Failure/retry recovery, optional residency/resource controls, other models, GPUs
and Unraid versions are not covered exhaustively. Test or narrow relevant claims.
Do not mark the entire acceptance protocol complete from one model installation.

The Vulkan branch relies on two facts checked from sources, not on a server.
Unraid's `/dev/dri` nodes belong to group `video` (GID 18) unless the ich777
GPU plugins open them. The upstream image's Mesa drivers cover AMD and Intel
but not NVIDIA. See the [Vulkan notes](CONFIGURATION.md#vulkan-variant).

The sequence follows [CA submission guidance](https://ca.unraid.net/submit/help):
public active repository, OSI-approved root licence, profile/template metadata,
then Validate/Scan.

## Repository contents

The publication test in `tests/test_publication.py` holds the exact list of
files that belong in the repository and compares it with Git's file inventory.
Add a new file to that list only after a publication-safety review.

Never include the parent checkout/history, `speak.sh`, `.devops/unraid`, SSH/API
credentials, test harnesses, raw Docker inspections, WAVs/screenshots, downloaded
models, personal configuration or original icon pack. Reports under
`docs/reports/` contain selected technical evidence. Raw artifacts stay outside
the repository.

## Local review procedure

Run `python3 -m unittest discover -s tests -v` from the repository root. The
checks cover template structure, the file inventory, relative documentation
links, CI policy text and selected accidental-data patterns. They are not a
complete secret scanner, legal clearance, CA validation or proof of current
upstream compatibility. GitHub Actions runs the same tests on every push and
pull request. No image build, custom CI credentials or server access is required.

## GitHub publication record

Published September 13 (Europe/London).

- Public repository: [lozenge0/audio-cpp-unraid](https://github.com/lozenge0/audio-cpp-unraid),
  default branch `main`, Issues enabled.
- Fresh signed root commit `d40ecdfe65dc24509d144264c289ac51e06223c2` with no
  parent history. Author and committer use the owner's GitHub noreply identity.
  GitHub reports the signature verified.
- [First hosted validation](https://github.com/lozenge0/audio-cpp-unraid/actions/runs/34725657862)
  passed. The first Dependabot Actions update check also completed. No custom CI
  secrets, image builds or server access were added.
- Workflow token default is read-only. Actions cannot approve PRs. Fork workflows
  require approval for all external contributors. Private vulnerability reporting,
  secret scanning and secret push protection are enabled. Auto-merge is disabled.
  `main` is protected by the "Template and publication checks" status.
- Public repository, Issues and advisories links returned HTTP 200. Downloaded
  README/template/profile/icon hashes matched local files. This does not validate
  the CA UI or public branch picker.

The first commit and CI timestamps are September 12 in UTC (after midnight
September 13 locally). Dated runtime evidence has not been rerun for publication.
No Unraid operations were performed.
