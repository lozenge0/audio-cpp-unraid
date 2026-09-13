# Controlled CUDA 13 image update and rollback

Prepared 2026-09-09; executed and verified 2026-09-10.

## Outcome and scope

An isolated test successfully ran a newer official CUDA 13 image against its
existing model files, then returned to the retained previous container/image.
Short and long API speech, native Studio generation, CUDA computation, health
and data-integrity checks passed on both versions.
Independent post-test review confirmed the restored configuration, matching
storage manifests, all six valid audio files, and fresh post-rollback CUDA logs.

This is a **manually controlled image update and retained-container rollback**.
It does not validate CA's scheduled updater, DockerMan's complete update flow,
template migration or fresh recreation of the old image during rollback. The
saved Unraid user template intentionally stayed on the original pinned image.
The separate [same-image recreation test](RECREATION-TEST.md) covers replacing
the original container object.

## Images

| Role | Official image digest | Upstream revision |
| --- | --- | --- |
| Original and final restored image | `sha256:f89dfcdccd5d54755fde3e670abd2a29d1ddc83df7aedc27a4bef83c9bffd45d` | `b0757573c90bf3ada5cf8ffbc69f3ab80a7a6947` |
| Newer candidate | `sha256:e041aeccc439a7801bcc5766b69361eb5a2aece350504f302305f3103ad8dcd7` | `05f9c5d6e26b6a06d7d29f0c8142a1c8951d9598` |

Both use `ghcr.io/0xshug0/audio.cpp`. Source and actual pulled-image metadata were
checked before deployment. The candidate includes the upstream Pocket TTS CPU
fix, but this CUDA test does not establish that the CPU short-text case is fixed.

## Safety and settings

Independent subagent review covered source compatibility and the deployment
harness before execution. The review identified an explicit exposed-port field
needed by the Engine API; it was added and verified before startup.

Only the isolated CUDA 13 test was stopped. Its model directory was copied to
a new dedicated backup while quiescent. File hashes, numeric owners, modes and
entry types matched between the original and backup. The original container
was renamed and retained stopped while the candidate used the normal test name.

The candidate inherited its own image defaults. Only six existing user
environment values (Unraid host metadata, timezone, GPU visibility/capabilities),
Unraid management/WebUI labels, process user, server command and container host
settings were carried over. Old CUDA-library environment variables and old OCI
image labels were not copied into the new image.

The test preserved UID/GID 99:100, NVIDIA runtime, the selected RTX 3060,
`compute,utility`, bridge networking, host port 18081 and the sole dedicated
model mount. Privileged mode and automatic restart remained disabled. A strict
pre-start check paused on Docker's `OomKillDisable` null-to-false normalization;
only that known default-equivalent difference was independently reviewed and
accepted. All other compared HostConfig settings had to match.

The personal service, CPU test and CUDA 12 test retained their original IDs,
configuration and stopped state. Their snapshots and the unchanged Unraid user
template were checked throughout. Global updater settings were not changed and
no global update job was invoked.

## Speech and persistence results

| Phase | Request | Voice | WAV size | Duration |
| --- | --- | --- | ---: | ---: |
| Updated image | API `hello` | Stock Alba | 30764 bytes | 0.64 s |
| Updated image | API longer sentence | Stock Alba | 211244 bytes | 4.40 s |
| Updated image | Studio longer sentence | `demo_1_man` | 230444 bytes | 4.80 s |
| Restored image | API `hello` | Stock Alba | 30764 bytes | 0.64 s |
| Restored image | API longer sentence | Stock Alba | 222764 bytes | 4.64 s |
| Restored image | Studio longer sentence | `demo_1_man` | 230444 bytes | 4.80 s |

All six files decoded as non-silent mono 24 kHz PCM16. No subjective listening
assessment was performed by the harness. Studio returned HTTP 200 and used its
native Save WAV action, seed 1234, max_tokens 1024 and frames_after_eos -1.
API requests inherited upstream defaults for those omitted options. These are
functional checks, not comparative benchmarks or a full voice/model test matrix.

Both processes initially had empty dynamic model registrations. The API loaded
the existing Pocket TTS GGUF from the persistent mount before generation; no
model download was performed. Weights, stock embedding, package metadata,
owners and permissions matched the pre-update manifest after both phases.
The backup also remained identical. This does not prove JSON-based automatic
registration; that remains a separate test.

Fresh logs in each phase confirmed RTX 3060 detection, CUDA backend loading and
CUDA graph compute warmup. Both phases ended with healthy CUDA status and one
loaded model. Existing driver-init and legacy model-spec warnings remained.

## Rollback and retained state

After candidate testing, only that exact candidate was stopped and removed,
without deleting model storage or images. Its logs and inspect data were saved.
Because model data remained unchanged, backup restoration was unnecessary;
the test would have paused before rollback if data differed.

The original container was renamed back and started. Its original ID, image,
Config and HostConfig were verified. The final isolated test is running on the
**original** pinned CUDA 13 image, not the candidate. No rollback-named container
remains. The approximately 128 MiB model backup and both official images are
retained; neither was deleted or pruned.

Private evidence remains outside this public repository candidate under
`build/unraid-ca-validation/update-cuda13-20260909/`. Generated WAVs/screenshots
are in its parent directory with `cuda13-upgraded-` or `cuda13-rollback-` prefixes
and the date `20260910`. The harness and personal test settings are not shipped
as community-app runtime code.

Remaining gates include the fixed CPU image retest, optional persistent JSON,
public CA branch-selector validation, and the actual Unraid updater workflow.
