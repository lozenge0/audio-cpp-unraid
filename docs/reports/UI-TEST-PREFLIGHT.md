# Unraid UI validation preflight — 2026-09-07

## Result

Read-only checks passed on Unraid 7.3.2 with Community Applications 2026.07.21.
The existing personal service remained running and healthy with its container
identity unchanged. No isolated test container existed, and the selected test
port was free. Docker image storage had approximately 67 GiB available; cache
storage approximately 816 GiB. The retained official CPU/CUDA images and test
models were available. No deployment or server configuration writes were made.

Two prerequisites affect the next UI tests:

1. The administration interface redirects unauthenticated requests to `/login`.
   SSH access does not authenticate a browser. Continue with the owner logged
   into their browser and guided UI steps, or a separately approved interactive
   browser login. Do not ask for passwords in chat or bypass authentication.
2. The installed CA private-app scanner does not expand `Branch` elements.
   Three pre-expanded private test XMLs can exercise each variant's installation
   form and DockerMan handoff, but cannot validate the public one-template
   hardware selector. Keep that selector as an explicit release gate.

## Installed-source evidence

- `include/paths.php`, line 67: `convertedTemplates` points to
  `/boot/config/plugins/community.applications/private/`.
- `include/exec.php`, `getConvertedTemplates()`, lines 487–533: reads
  `private/*/*.xml` and adds one private app per file, without branch expansion.
- `include/helpers.php`, `fixTemplates()`, line 398: normalizes metadata and
  configuration descriptions; it does not expand branches. `addMissingVars()`
  supplies absent fields, not branch records.
- `include/exec.php`, `DownloadApplicationFeed()`, lines 374–413: expands
  feed-provided branches and generates the `BranchID` records used by the picker.

These observations are specific to the installed version. Upstream development
code may differ. Independent subagent source review confirmed the distinction
between private installation tests and feed-based branch-selector acceptance.
Do not modify CA plugin code or inject synthetic branch records into its live
cache to represent a supported installation test.

## Proposed continuation

- With the owner authenticated, stage isolated pre-expanded private test XMLs
  using a unique repository directory, separate test name/port and per-variant
  model storage. Do not replace any existing private or user template.
- Inspect each actual CA installation form before applying. Retain upstream
  moving tags for form inspection, then select recorded immutable upstream
  digests for controlled runtime tests. Record that difference in the evidence.
- Run one test container at a time. No production mappings, global updater
  changes, driver changes or test autostart entries.
- The host has global container updates enabled; do not invoke a global update
  job to test one container. Pin controlled experiments and review the specific
  single-container update/recreation path before use.
- Test distinct upstream image versions and rollback against isolated data,
  preserving the Docker user/group and selected GPU settings. Same-image
  recreation alone is not image-upgrade or unattended-update acceptance.
- Validate optional owner-provided upstream JSON separately, including stable
  model IDs and read access under UID 99/GID 100.
- Validate the public branch selector later through a supported feed/preview
  workflow. Publication, submission or coordination needed to access that
  workflow requires explicit owner approval.

No UI install, new runtime inference, upgrade, rollback or JSON persistence
test was completed during this preflight.

## Private entries staged — 2026-09-07

After the owner logged into Apps in their own Brave browser, an independently
reviewed generator produced three pre-expanded test copies outside this public
repository candidate. Copies were staged only in the new private repository
directory `/boot/config/plugins/community.applications/private/audio-cpp-ca-ui-test/`.
Local and server SHA256 checksums matched for all three files.

The test names are `audio-cpp-test-cpu`, `audio-cpp-test-cuda12` and
`audio-cpp-test-cuda13`. They share test port 18081 (only one may run at a time),
with fresh per-variant model paths under the separate UI-test storage root.
No model directories or containers were created by staging. The existing
personal container remained healthy and unchanged. No global updater settings
or existing templates were modified.

Next owner action: return to Apps Home, open Private Apps and choose the CPU
test's Install action, stopping before Apply. Confirm the actual form's name,
port, model mapping and Extra Parameters, then pin the reviewed image digest.
Do not use Edit/Update on an entry associated with the existing service. This
staging step is not evidence of UI installation or runtime acceptance.
