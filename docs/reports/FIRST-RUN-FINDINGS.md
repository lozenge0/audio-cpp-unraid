# First-run validation: model-directory permissions

Follow-up: the isolated native Docker `--user=99:100` experiment subsequently
passed model download/inference checks for CPU, CUDA 12 and CUDA 13, with lifecycle
checks. See [user-identity test results](USER-IDENTITY-TESTS.md). The original
failure below remains the historical baseline. The local template adopted the
tested override on 2026-09-07; full CA installation/update acceptance is pending.

## Result — 2026-09-06

**The original template-only fresh installation was blocked at model download.** The
unmodified CPU server starts and serves its native WebUI, but cannot write to
the model directory created by DockerMan on the tested Unraid 7.3.2 host.
No permission workaround or application change had been applied in this phase.

| Check | Result |
| --- | --- |
| Independent test-template isolation review | Passed |
| Target DockerMan rendering, CPU/CUDA12/CUDA13 | Commands inspected; expected ports, mounts and backends |
| CPU server startup and HTTP health | Passed; backend cpu, zero registered models |
| Native WebUI in headless Chrome | Studio and model library rendered successfully |
| Fresh model directory | UID 99, GID 100, mode 0755 |
| CPU image process | UID 1000, GID 1000 (`ubuntu`) |
| Write-access check as image user | Failed |
| Browser PocketTTS English Q8 download | Failed: `could not create package staging directory` |
| Downloaded model bytes | 0 |
| CPU inference, CUDA runtime tests, persistence and image upgrade | Not reached in this phase |

## Reproduction and image identity

The generated test copies used a separate container name, unused host port and
fresh per-variant appdata path. The public template was not installed over an
existing service. DockerMan's `xmlToCommand(..., true)` created the model directory
using its normal `mkdir(..., 0777)` plus ownership 99:100. The host's php-fpm mask
was 0022; the test helper matched that mask, resulting in mode 0755. These are
observed host settings, not a claim that every Unraid installation is identical.
The bind mount hides the image's own `/app/models` directory and its baked-in
`ubuntu` ownership. The package manager needs to create a staging subdirectory
inside that mount. Independent source review confirmed this matches the observed
failed write check and browser error.

The actual container command matched the reviewed CPU rendering except for using
the pulled immutable image digest during this diagnostic session. The host has
global container auto-updates enabled, so a fixed digest prevented a rolling image
change during testing. The public template still follows the moving upstream tag.
This test did not exercise the real CA branch-selector UI or its update workflow.

- Upstream tag pulled: `ghcr.io/0xshug0/audio.cpp:full-cpu`
- Digest: `sha256:8aeff0a079f188c5917781a9f9cc59ccc1d30fd3111a472cec3962ed4ed649c1`
- Image source revision: `b0757573c90bf3ada5cf8ffbc69f3ab80a7a6947`
- Image creation label: `2026-09-06T07:59:32Z`
- Image size reported by Docker: 760161173 bytes (shared layers may reduce disk use).

Through the native model library, the browser selected Pocket TTS / GGUF Q8 and
confirmed its download. The UI displayed FAILED and the staging-directory error.
The model manager reported package `pocket_tts_english_q8_0`, state `failed`, exit
code -1 and downloaded_bytes 0. The target remained at its original permissions.

## Options recorded after the baseline failure

Option 1 was subsequently approved, tested and adopted in the local template;
the original alternatives below are retained as the decision record.

Choose how the public integration should provide writable model storage while
retaining the upstream image:

1. Investigate Docker's native `--user=99:100` override as a template-only option
   matching the fresh folder owner. It leaves upstream image contents unchanged,
   but downloads, temp/cache paths, file modes, persistence and NVIDIA access
   under the changed identity all require testing before calling it a fix; or
2. Document a one-time, narrowly scoped ownership/permissions setup for the
   selected new model directory, then validate that installation path; or
3. Seek an upstream/container integration improvement before claiming a smooth
   first-run installation. Potential alternatives need their own review/testing.

Do not silently run the application as root, add a wrapper, recursively loosen
appdata permissions, or change an existing shared directory.

The temporary test container was stopped and removed after evidence collection.
Its small harness/fresh appdata and pulled CPU image were retained; no model
weights were downloaded. The production service remained running and healthy.
No driver, host Docker settings, global updater settings or production appdata
were changed.
