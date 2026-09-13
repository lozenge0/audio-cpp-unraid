# CUDA 13 same-image recreation — 2026-09-09

## Outcome

The isolated CUDA 13 container was stopped, removed without deleting volumes,
and recreated using the same official image and persistent model storage.
API and browser speech generation passed after replacement, without model
redownloads. This validates same-image replacement, not a newer-image upgrade,
rollback, scheduled update or the CA public branch selector.

The owner approved this exact test. Independent subagent review preceded the
destructive step and reviewed the one Docker default normalization described
below. The personal service and other test containers remained unchanged.

## Image, settings and preservation

- Official image digest:
  `sha256:f89dfcdccd5d54755fde3e670abd2a29d1ddc83df7aedc27a4bef83c9bffd45d`.
- Upstream revision: `b0757573c90bf3ada5cf8ffbc69f3ab80a7a6947`.
- New container ID differs from the original; its image ID is identical.
- UID/GID 99:100, NVIDIA runtime, selected RTX 3060, `compute,utility`, bridge
  port mapping, sole model mount, server arguments, environment and labels were
  preserved. The original effective logging settings and pids limit were also
  retained, not added to public template defaults.
- Before/after manifests matched for every model file's SHA256, file/directory
  sizes, owners and modes, including package metadata and the Alba embedding.
- The saved Unraid user template remained byte-identical. Config, HostConfig
  and State of the personal service and two other audio.cpp tests were checked
  against their snapshots; none were changed by this operation.
- No image pull, model download, ownership change or global updater change was
  made. Original container logs and configuration were preserved locally before
  removal; only the replaced container's disposable writable layer was removed.

## Exact configuration checks

A preliminary CLI creation command was rejected during independent review:
plain Docker create would change stdout/stderr attachment flags compared with
DockerMan's detached launch. The final method used the Docker Engine's create
endpoint with the saved Config/HostConfig, then inspected the replacement before
starting it. This endpoint does not pull an image or start a container.

All Config fields matched except the generated hostname. The strict HostConfig
check paused startup on one representation difference: `OomKillDisable` changed
from null to false. Independent review confirmed both preserve default OOM
killing; an explicit true value was not permitted. Only this null-to-false
normalization was accepted, with all other HostConfig fields compared exactly.
The replacement was then started and passed post-start integrity checks.

## Inference evidence

After replacement, `/health` returned `ok` with backend `cuda`, while `/v1/models`
was initially empty. The test registered the existing Pocket TTS GGUF through
the upstream API, without downloading anything. This is expected UI-only
behavior: persistent weights do not imply persistent dynamic registration.

| Test | Voice | Result |
| --- | --- | --- |
| API longer sentence | Stock Alba | 207404-byte WAV, 4.32 s, non-silent |
| API `hello`, after longer sentence | Stock Alba | 30764-byte WAV, 0.64 s, non-silent |
| Native Studio longer sentence | `demo_1_man` | HTTP 200, saved WAV, 4.80 s |

All outputs decoded as mono 24 kHz PCM16. API RMS values were approximately
4672 and 2536; no subjective listening evaluation was performed in this phase.
Studio used seed 1234, max_tokens 1024 and frames_after_eos -1, as captured from
the actual request. API tests omitted those options and inherited defaults.

Logs confirmed RTX 3060 detection, `libggml-cuda.so` loading and CUDA graph compute
warmup. The server remained healthy with Pocket TTS loaded after inference.
Existing driver-initialization and legacy model-spec warnings remained; the
successful results do not imply all similar warnings are harmless.

## Evidence and remaining work

Private snapshots, request harness, logs, checksums and replacement payload are
under `build/unraid-ca-validation/recreate-cuda13-20260909/` in the surrounding
development checkout. WAVs and the Studio screenshot use the
`cuda13-recreated-*-20260909` prefix in its parent directory. These are testing
artifacts, not code or personal configuration shipped by the community app.

The recreated CUDA 13 test remains running on the isolated test port. The old
container object no longer exists; saved settings, unchanged official image
and retained model storage allow another recreation if necessary.

Next lifecycle gate: distinct official-image update and rollback, separately
reviewed and authorized. Do not reuse this same-image payload for upgrades: it
copies inherited environment/labels and would incorrectly preserve metadata or
library defaults from the old image. Use the saved user template's actual
overrides with each new image's own defaults.
