# Implementation plan

## Decisions fixed by the project owner

- Project: audio.cpp for Unraid; standalone repository: audio-cpp-unraid.
- GitHub owner: lozenge0; integration support: repository GitHub Issues.
- Artwork provenance: owner confirms original Claude/AI generation from their
  own prompts. MIT for integration files and CC0 for the icon approved 2026-09-12,
  with the artwork dedication limited to whatever rights the owner holds.
- No personal code/configuration, upstream fork, custom image or runtime wrapper.
- Current template: CPU base, CUDA 12 and CUDA 13 branches. Upstream now has a
  Vulkan Docker build; adding a branch awaits separate integration/hardware review.
- Follow moving upstream Docker tags. No independent image release pipeline.
- Standard Unraid controls plus optional upstream CLI/user-owned JSON.
- Native Docker `--user=99:100` in every variant, following successful isolated
  download/inference tests; no ownership-changing helper or `PUID`/`PGID` mapping.
- Draft first release v0.1.0; stable integration v1.0.0 after validation.

## Current publication status

The standalone GitHub repository and CI are live. The owner reports CA submission
and auto-approval; catalog visibility and public installation remain unverified.
The beta template requests AI and Tools categories. See RELEASE-REVIEW.md for the
current evidence and remaining checks. No production migration has been performed.

## Runtime progress recorded on 2026-09-12

The local template now includes the successfully tested Docker user/group setting.
Isolated CPU/CUDA 12/CUDA 13 downloads and browser/API inference passed; CPU/CUDA 13
restart and CUDA 12 recreation checks passed. See USER-IDENTITY-TESTS.md for the
tested images and limits. Subsequent pre-expanded private CA UI tests, controlled
CUDA 13 recreation/update/rollback, and the fixed official CPU short-text/streaming
retest have passed within their documented scopes. See VALIDATION.md and
CPU-RETEST-20260912.md. The public branch selector, scheduled updater and remaining
release checklist are still pending. No publication or migration of the existing
personal deployment has taken place.
The owner confirmed successful playback on the fixed CPU image. The reconciled
status, publication file list and remaining decisions are in RELEASE-REVIEW.md.
Read-only UI preflight found two prerequisites: owner browser authentication and
a supported feed/preview route for the branch picker. Installed CA private apps
can test pre-expanded variants but not the selector. See UI-TEST-PREFLIGHT.md.

## Stage 1 — local preparation

Prepare standalone metadata, template, supplied icon, documentation and local
structural tests. Independently review the template and preserve the current
personal deployment. No Git repository has been created or published by this step.
Review completion is recorded separately from live deployment acceptance.

## Stage 2 — isolated validation (partially complete)

Agree on a separate test-container name, unused port and fresh dedicated appdata
directory; never inherit production paths or replace the existing audio-cpp
container. Check available disk space before pulling more CUDA images. Run the
checklist in VALIDATION.md, including real CA branch expansion/DockerMan rendering,
empty-directory permissions, browser downloads, CPU and both CUDA inference,
model/config persistence, and image update/rollback. Use safe test workloads
compatible with the other GPU users. Record exact images/models and results.

The initial fresh-directory permission failure was resolved in isolated tests
using Docker `--user=99:100`; the local draft now includes it in all variants.
Public branch selection, full DockerMan/scheduled updates and broader compatibility
checks remain; controlled CUDA 13 update/rollback is already recorded as passing.
If a storage layout or future image fails, review it before changing identity
or permissions. Do not silently add root execution, recursive broad ownership
changes, or startup helpers. CPU/CUDA13 cannot be advertised as tested merely
because the earlier personal CUDA12 service works.

## Stage 3 — publication identity and beta

GitHub publication, support URLs, CI and MIT/CC0 terms are recorded. The owner
reviewed the repository and subsequently submitted it to CA. Follow PUBLISHING.md
for the repository setup record. Confirm app/container naming and category in
the public listing. Local SVG checks at 32/48/180 px on light/dark backgrounds
passed; actual CA rendering and full deployment acceptance remain pending.

## Stage 4 — Community Apps submission

The owner reports automatic approval. Confirm catalog visibility and review
Validate/Scan results; rerun those checks after meaningful XML changes. Do not
create a duplicate submission because the listing is not yet visible. Preserve
tested-combination limits, maintenance/support boundaries and rollback guidance.

## Ongoing maintenance

Upstream images update independently. Monitor changes to launch arguments,
permissions, storage, driver requirements and security; update template/docs when
needed. Changes that affect existing installs need explicit migration instructions.
No remote access to other users' servers is required. Release-only image tags
would be a separate upstream request if desired. Vulkan integration is a separate
review of the now-existing upstream build, not a reason to build our own image.

## Approval boundaries

Local draft preparation and local tests are in scope now. Deploying test containers,
altering the live service, creating/pushing a public GitHub repository, contacting
upstream, submitting to CA, or granting publication rights are separate decisions.
The owner approved the isolated baseline/user-identity experiments already
recorded, followed by local template adoption and review. Those approvals do not
authorize production migration, publication or changes to global updater settings.
