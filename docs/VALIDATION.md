# Validation and release acceptance

This integration is under development. Source inspection and XML checks do not
establish that its installation flows work. Record the date, Unraid and
Community Applications versions, image digest, hardware, model package and
results for each runtime test below.

## Current acceptance summary — 2026-09-12

Use [RELEASE-REVIEW.md](RELEASE-REVIEW.md) as the current publication tracker.
The numbered checklist below is a reusable acceptance protocol, not a per-image
completion ledger: unchecked boxes do not negate the scoped successes here, and
passing one variant does not complete every clause for all variants.

| Check group | Current status |
| --- | --- |
| Local XML / complete variants / native settings | Passed local checks and reviewed private installation forms |
| Fresh storage / Pocket TTS download | Passed on recorded CPU/CUDA images with 99:100 |
| CPU short-text inference | Fixed image passes API, Studio, streaming and restart; owner playback confirmed |
| CUDA 12 / CUDA 13 inference and restart | Passed on recorded images and RTX 3060 |
| Recreation | Passed controlled CUDA 12/13 tests, not all lifecycle paths |
| Image update / retained-container rollback | Passed controlled CUDA 13 test, not full DockerMan or scheduled updates |
| Public branch selector / variant switching | Pending supported workflow validation |
| Optional JSON / residency limits / failure recovery | Incomplete; personal deployment results do not substitute |
| Artwork / licensing / public links / CA scan | MIT/CC0 approved September 12; local artwork/metadata review and September 13 live-link checks passed; actual CA rendering and CA scan pending |

The owner confirmed the fixed CPU test is "working well". No new runtime tests
or server changes were made during this documentation reconciliation.

## Current runtime finding

### Fixed official CPU image retest — 2026-09-12

Today's official `full-cpu` image, pinned at revision `5bea9c7`, passed repeated
`hello` and longer speech in offline API, native Studio and explicit model-streaming
tests, including a fresh-process repeat. Model hashes/permissions and all saved
Unraid configurations were preserved. See [CPU retest results](reports/CPU-RETEST-20260912.md).
The specific short-text crash gate is cleared for this tested image/model/host;
full release acceptance is not implied. Current Studio offers Alba for Pocket TTS;
the former male demo voice passed API/streaming tests separately.

The separate CPU retest is now running on port 18081. The earlier CUDA 13 test
was stopped and retained to free that port; the personal container remains untouched.

### Controlled CUDA 13 update/rollback — 2026-09-10

The independently reviewed isolated image update and retained-container rollback
passed short/long API speech, Studio generation, CUDA computation, configuration
and model-data checks. See [full results](reports/UPDATE-ROLLBACK-TEST.md). The original
pinned CUDA 13 test was restored and running at that test's completion; it was
later stopped for the September 12 CPU retest. This is not CA scheduled-updater
or full DockerMan-update acceptance.

### CUDA 12 owner-operated UI test — 2026-09-09

The owner installed the pre-expanded private CUDA 12 template through CA's
actual installation form, with its repository changed to the recorded immutable
upstream digest `sha256:595cd56bc11dcb855b6cbca7fbd2b82f44055515dc16f353db7b2d43037c9498`.
This is revision `b075757`, matching the failing CPU image's source revision.
Independent template review and server isolation checks preceded installation.

The owner reports that native Pocket TTS GGUF Q8 download and Studio generation
of both `hello` and a longer sentence with the default male voice succeeded.
Post-test inspection confirmed:

- Container remained running; `/health` returned `ok`, backend `cuda`, one model.
- `/v1/models` showed Pocket TTS loaded from the intended persistent model mount.
- Logs loaded `libggml-cuda.so`, detected RTX 3060 compute capability 8.6 and
  recorded CUDA graph compute warmup. NVIDIA reported an `audiocpp_server`
  process using 978 MiB at inspection time (not a peak-memory measurement).
- User/group remained 99:100; model directory mode 0755, GGUF mode 0644.
- GGUF SHA256 was `0315406421d515d9ffbde49ed998832ff2962562ef8abde440c85fa0a27d8b2a`,
  identical to the CPU test model. Port and model mapping remained isolated.

Audio playback success is owner-reported; this phase did not independently
capture WAVs or full request payloads, streaming mode, seed or the longer text.
It supports a CPU-specific problem in the tested revision, not a fully controlled
cross-backend reproduction or complete CUDA acceptance. Existing driver-init
warnings remained despite successful reported inference. Later lifecycle evidence
is recorded separately; this inference test alone did not validate version
update/rollback, optional JSON or the public branch selector.

Follow-up restart: the owner reported restarting the CUDA 12 test through Unraid,
selecting the retained model and successfully generating speech without another
download. Inspection confirmed the new process start at 2026-09-09 11:12:10 UTC,
healthy CUDA backend, loaded Pocket TTS, unchanged GGUF checksum and user 99:100.
This covers owner-operated restart and model reuse, not automatic restoration
of dynamic model registrations or image replacement.

After independent CUDA 13 preflight review, only the verified CUDA 12 test
container was stopped to release port 18081. It exited cleanly (0); its container
and downloaded files were retained. The personal service remained stopped and
unchanged. The staged CUDA 13 template matched its reviewed checksum, its model
path was absent, and its retained pinned image matched revision `b075757`.
CUDA 13 UI installation then proceeded as recorded below.

### CUDA 13 owner-operated UI test — 2026-09-09

After screenshot review, the owner installed the private CUDA 13 test through
Unraid's form. Inspection confirmed pinned upstream digest
`sha256:f89dfcdccd5d54755fde3e670abd2a29d1ddc83df7aedc27a4bef83c9bffd45d`,
revision `b075757`, user 99:100, NVIDIA runtime, the selected RTX 3060 UUID and
`compute,utility` capabilities. Port 18081 and the fresh dedicated CUDA 13 model
mount matched the reviewed test settings; privileged mode was disabled.

The owner reports successful native Pocket TTS GGUF Q8 download and playback
of `hello` and a longer sentence with the default male voice. Subsequent checks
confirmed a running container, healthy CUDA backend and loaded Pocket TTS model.
Logs show RTX 3060 detection, `libggml-cuda.so` loading and CUDA graph compute
warmup. Model-directory ownership/mode remained 99:100/0755 and GGUF 99:100/0644;
the GGUF hash matched the CPU/CUDA 12 value recorded above.

Playback is owner-reported; exact request payloads and WAV files were not
captured in this phase. Driver-init and legacy model-spec warnings persisted.
The owner subsequently reported a successful restart and model reuse without
redownloading. Inspection before the recreation phase confirmed the new process
start and retained settings. The separately approved same-image recreation also
passed API/browser inference and integrity checks; see
[recreation results](reports/RECREATION-TEST.md). Distinct-image updates, rollback and
JSON persistence remain separate acceptance gates.

### CPU failure and follow-up

**New CPU acceptance failure — 2026-09-07:** after installation through the
owner's actual CA/DockerMan UI and pinning the recorded CPU digest, Pocket TTS
GGUF Q8 downloaded successfully. The owner's Studio request then crashed the
server at 15:15:34 UTC: exit 139, `OOMKilled=false`, with
`ggml-backend.cpp:1982: GGML_ASSERT(tensor->buffer == NULL) failed`.
The browser displayed “Failed to fetch” because the server had exited.
Model and Alba SHA256 hashes match the earlier successful isolated files;
effective UID/GID, model mapping and CPU arguments were correct. This is not
a successful end-to-end UI acceptance test. Earlier passing requests do not
establish reliability across prompts or streaming modes.

Independent source review identified a possible repeated tensor-view
initialization in the Pocket TTS CPU decoder. The same sequence was confirmed
in upstream revision `b0757573c90bf3ada5cf8ffbc69f3ab80a7a6947`.
The owner subsequently identified the failing text as `hello` with the default
male voice and reported longer text working. Full request options and streaming
mode were not captured. No restart, image replacement or source fix was performed
during the initial diagnosis.

Upstream subsequently fixed the matching CPU view-initialization defect in
[commit 88107a4](https://github.com/0xShug0/audio.cpp/commit/88107a4344778b8befa0aac25cf5b47d0274ca63)
on 2026-09-08; [issue 488](https://github.com/0xShug0/audio.cpp/issues/488) reports
the same assertion outside Unraid. At the 2026-09-09 registry check, `full-cpu`
still referenced pre-fix revision `9c6a282`. A later registry check on 2026-09-09
found the official CPU image at revision `05f9c5d`, including the fix, with digest
`sha256:370e71fc53d921f42ad48a40278443cd0bff87e96988f7e6ad571e463a056499`.
Neither upstream acknowledgement nor the CUDA pass validates the fix for our
short-text CPU case. That block was subsequently cleared for the tested September
12 image by the [fixed-image retest](reports/CPU-RETEST-20260912.md), not by source review alone.

The isolated CPU fresh-install test on 2026-09-06 started successfully and the
native WebUI rendered, but browser model download failed because DockerMan's
99:100/0755 model directory was not writable by the image's UID 1000 user.
See [first-run findings](reports/FIRST-RUN-FINDINGS.md) for exact image identity and
evidence. A subsequently approved `--user=99:100` experiment passed browser
downloads, browser/API inference for all three variants, CPU/CUDA13 restart and
CUDA12 recreation checks. See [user-identity results](reports/USER-IDENTITY-TESTS.md).
The local draft adopted the override in all three variants on 2026-09-07, with
matching structural checks and setup guidance. Subsequent private UI and controlled
CUDA 13 lifecycle results are recorded above. Full acceptance remains incomplete;
the protocol below is not a claim that every clause has been completed.

## Local identity-adoption review — 2026-09-07

- CPU Extra Parameters: `--user=99:100`; both CUDA branches:
  `--user=99:100 --runtime=nvidia`. Upstream images, application arguments and
  complete per-branch configuration fields remain unchanged.
- All 16 maintainer structural tests passed, including regression checks for
  missing/changed identity and unsupported `PUID`/`PGID` variables across every
  resolved variant. Setup descriptions explicitly identify the effective user.
- A separate review found no blocking issues and passed the structural tests.
  It checked fresh versus existing storage, update/rollback identity
  preservation and limits of the recorded one-host runtime evidence. Its wording
  suggestion was applied to distinguish pending CA installation acceptance from
  the isolated download/inference tests already completed.
- This phase changed only local template/docs/tests: no server commands,
  deployments, permission changes, image pulls or publication were performed.
  It does not substitute for the remaining runtime release gates below.

## Local draft review — 2026-09-06

- 12 maintainer structural tests passed, including three resolved variants and
  negative checks for partial branch fields, custom runtime wrappers and personal
  tuning. This models reviewed branch semantics; it does not execute CA itself.
- A separate review found no XML/profile defects. Documentation was
  corrected to separate HTTP health from Docker healthcheck status and to require
  a unique test name, port and storage directory.
- Supplied SVG artwork and metadata are preserved (a final newline was added).
  Owner confirmed generation from their own prompts using Claude/AI. Visual
  rendering and publication/reuse-licensing approval were pending at this review.
  Update September 12: MIT/CC0 approved; local visual/metadata review passed.
  September 13: GitHub draft published; actual CA rendering remains pending.
  See RELEASE-REVIEW.md for the publication verification record.
- GitHub destination is lozenge0/audio-cpp-unraid with repository Issues for
  support. September 13: public metadata URLs and remote file hashes verified.
- No test container was deployed, registry image pulled, live service changed,
  GitHub repository published or CA submission made by this preparation stage.

## Existing evidence and its limits

The earlier personal deployment on Unraid 7.3.2 used an RTX 3060 with 12 GiB of
VRAM, an explicitly pinned CUDA 12 image and a prepared server configuration.
That deployment produced speech using CUDA and was checked for restart
persistence and idle unloading. Its appdata ownership was prepared explicitly.

Those results support the feasibility of running audio.cpp on this server.
They do not validate this integration's branch selector, empty-appdata setup,
CPU image, CUDA 13 image, or future image updates. All variants of the new
template need the checks below. Do not mark a new check complete solely because
the personal deployment passed a similar check.

## 1. Template and branch checks

The [UI preflight](reports/UI-TEST-PREFLIGHT.md) found that installed CA 2026.07.21 private
apps do not expand branches. Pre-expanded private XMLs can test each variant's
installation handoff, but the public selector needs a supported feed/preview
workflow. An authenticated owner browser session is also required.

- [ ] Parse the XML and verify all repository references, required metadata,
  paths, ports and arguments. Resolve each image tag to a recorded digest.
- [ ] Expand the default CPU template and every CUDA branch using the supported
  CA branch semantics. Branch overrides replace complete fields: a branch's
  `Config` list must include every shared path and port it needs.
- [ ] Render every expanded template with the target Unraid DockerMan code,
  without creating host directories or containers. Inspect the resulting
  command and its argument boundaries.
- [ ] Verify that CPU installation needs no NVIDIA runtime, NVIDIA variables
  or GPU device mappings. Check that each CUDA installation selects the
  intended image, backend, runtime and user-supplied GPU identifier.
- [ ] Verify that the WebUI points to the configured host port. Record
  effective Docker restart, healthcheck and stop settings: this template adds
  none and should retain the image/Docker defaults. If testing optional user
  overrides, verify they survive the chosen branch configuration.
- [ ] Confirm only supported native DockerMan fields are presented. Do not
  imply that arbitrary environment variables configure audio.cpp CLI options,
  or that `PUID`/`PGID` changes image ownership.
- [ ] Check the branch selector in a supported CA feed/preview workflow. Confirm
  that the selected variant reaches the installation form with its complete
  settings. A passing local expansion test does not replace this UI check.

## 2. Fresh storage and installation

Before starting any test, choose a separate container name, an unused host port
and a new dedicated appdata directory. In particular, do not use the default
`audio-cpp` name on a server where the personal deployment already uses it.
Use fresh isolated storage for each fresh-install test. Preserve the existing
personal deployment and other containers.

- [ ] Inspect the selected image's default numeric UID/GID and the container's
  effective identity separately. Verify the resolved template and actual process
  use `--user=99:100` for every variant; do not assume image defaults are permanent.
- [ ] Test genuinely empty appdata with the documented setup procedure.
  Unraid can create directories as UID 99/GID 100, matching the draft's native
  Docker user override. Record owner, group and mode and verify writes as the
  container's effective user, including any required temporary/cache paths.
  Do not solve this by changing unrelated appdata
  permissions or advertising unsupported `PUID`/`PGID` variables.
- [ ] Start each variant with its separate test name, port and storage.
  Confirm HTTP `/health`, WebUI availability, expected backend and persistent
  model directory. HTTP health is distinct from Docker health status: the
  template does not configure a Docker healthcheck, so a `healthy` status is
  not required unless the image or user supplies a healthcheck.
- [ ] Install a small supported model through the browser, then confirm that
  its files and package metadata reside in the host model directory. Record
  the package version/revision, required disk space and license.
- [ ] Confirm install failures are visible and leave a recoverable state;
  check any documented retry or cleanup operation only against test data.

## 3. Inference and shared resources

- [ ] CPU: generate audio using the CPU image and explicit CPU backend.
  Validate the audio format, nonempty samples and audible output. Record
  latency and approximate host memory consumption.
- [ ] CUDA 12: generate audio with compatible host driver and GPU. Verify
  CUDA backend initialization and GPU activity attributable to this container
  during actual inference; health status and `nvidia-smi` alone are not proof.
- [ ] CUDA 13: repeat with that image and record driver/GPU compatibility
  independently. Do not infer success from the CUDA 12 test.
- [ ] Check both the browser and HTTP API, using the actual discovered model
  ID and supported voice. Record a minimal working API request.
- [ ] On a shared GPU, measure memory use and confirm the test has not
  interrupted other services. Exercise expected resource-limit failures in
  an isolated setting; do not deliberately exhaust the production server.
- [ ] Confirm default startup inherits upstream model-residency and idle
  settings; this template sets no limits or idle timeout. Separately test
  documented optional tuning for model limits and natural idle unloading,
  then verify inference reloads the model. Allow for the server's polling
  interval. Memory estimates do not reserve VRAM against other apps.

## 4. Persistence and lifecycle

- [ ] Restart the test container and confirm model files remain present.
  Separately check model registration and API usability: downloaded files
  persisting does not mean interactive model selections persist.
- [ ] Test any documented optional server JSON configuration, including
  stable model IDs, default voice and precedence of CLI arguments.
- [ ] Recreate the container with the same appdata mapping. Confirm the
  documented model-selection or configured-model behavior still works.
- [ ] Check manual graceful stop and restart. Record effective Docker
  restart behavior without assuming automatic restart: the template adds no
  restart policy. If the user enables Unraid autostart, validate it separately.
  If an image or user supplies a healthcheck, an unhealthy result does not by
  itself trigger a Docker restart policy.
- [ ] Verify how a user changes variants after installation. Changing an
  image tag alone does not add or remove GPU runtime settings. Preserve
  appdata and review the entire replacement container configuration.

## 5. Updates and rollback

Rolling tags can resolve to different images without changes to this template.
Maintain an evidence record of the exact digests tested for each variant.

- [ ] Before an upgrade, record the existing image digest and effective
  container settings; back up relevant configuration and package metadata.
  Keep a recoverable copy of mutable data if the update may migrate it.
- [ ] Test the candidate digest against copied test appdata. Repeat startup,
  browser/API inference, ownership and restart checks. Confirm `--user=99:100`
  and the selected variant's GPU runtime settings survive recreation/update.
- [ ] Test rollback to the recorded prior digest with compatible saved
  configuration/data. Reverting an image alone may not undo data changes.
  Preserve the matching process identity: image rollback is not an ownership
  migration, and reverting to UID 1000 may prevent writes to UID 99-owned files.
- [ ] Document any model/configuration incompatibility and update the tested
  version matrix before recommending the new image.

## 6. Network exposure and publication

- [ ] Confirm the intended host binding and mapped port. The server has no
  configured authentication; keep it reachable only by trusted clients.
  Model-management access includes downloading and deleting model packages.
- [ ] If remote access is required, validate an authenticated access boundary
  separately before exposing the service. Do not imply the WebUI supplies
  login protection.
- [ ] Remove personal IP addresses, GPU UUIDs and credentials from public
  defaults. Validate support links, icon, repository profile and license.
- [ ] Run CA's submission validation and scan on the proposed public
  repository, resolve findings, and review the final installation instructions.
- [ ] Obtain explicit publication signoff after reporting tested variants,
  limitations and outstanding issues. Preparing this project does not
  authorize publishing it or changing the running server.

## Evidence record

For each new variant/image test, copy and fill this blank record; completed
records are in the linked dated reports above. These placeholders are not current
project status.

| Field | Record |
| --- | --- |
| Test date and tester | Pending |
| Unraid / CA version | Pending |
| Image tag and digest | Pending |
| Backend / GPU / driver | Pending |
| UID/GID and directory preparation | Pending |
| Model package and license | Pending |
| Fresh install / browser install | Pending |
| Browser / HTTP inference | Pending |
| Restart / recreation | Pending |
| Optional idle/residency tuning | Pending |
| Upgrade / rollback | Pending |
| Limitations and unresolved failures | Pending |

## References

- [CA XML field reference](https://ca.unraid.net/submit/help/xml-field-reference)
- [CA repository and validation guide](https://ca.unraid.net/submit/help/repository-xml)
- [CA branch expansion implementation](https://github.com/unraid/community.applications/blob/master/source/community.applications/usr/local/emhttp/plugins/community.applications/include/exec.php)
- [DockerMan template rendering](https://github.com/unraid/webgui/blob/master/emhttp/plugins/dynamix.docker.manager/include/Helpers.php)
- [audio.cpp Docker documentation](https://github.com/0xShug0/audio.cpp/blob/main/docs/docker.md)
- [audio.cpp server documentation](https://github.com/0xShug0/audio.cpp/blob/main/app/server/README.md)
