# Native Docker user/group override: validation results

## Outcome — 2026-09-06

The isolated `--user=99:100` experiment succeeded for **CPU, CUDA 12 and CUDA 13**
on the tested Unraid 7.3.2 host. This resolves the observed fresh-directory write
failure for these tested combinations without changing upstream image contents,
running as root, adding a startup wrapper, or changing directory ownership/modes.

The local public-template draft adopted the override on 2026-09-07, with matching
structural checks and documentation. That local adoption is not a new runtime
test or a claim of complete Community Apps acceptance. The existing personal
deployment was not modified.

## Controlled change

The same isolated name/port scheme as the first-run test was used, with separate
fresh per-variant model directories. DockerMan created directories as 99:100 with
mode 0755 under the observed web-service mask 0022. Only the Docker process-user
setting was added: `--user=99:100`.

All variants reported `uid=99 gid=100(users) groups=100(users)`. The model mount
was writable. Downloaded files were owned by 99:100, with model files mode 0644.
No `chown`, `chmod`, extra supplementary group, privileged mode or root execution
was added. Temporary-directory write checks passed for CPU and CUDA 13; actual
native downloads/inference exercised the temporary path for all three variants.

The test used immutable upstream image digests to prevent the host's global
auto-updater from changing the experiment. The public draft retains moving tags.
No global update/autostart settings were changed; the temporary container was
removed after testing and was never added to Unraid autostart.

## Tested images and hardware

All images identify upstream revision
`b0757573c90bf3ada5cf8ffbc69f3ab80a7a6947`.

| Upstream tag | Tested image digest |
| --- | --- |
| `full-cpu` | `sha256:8aeff0a079f188c5917781a9f9cc59ccc1d30fd3111a472cec3962ed4ed649c1` |
| `full-cuda12` | `sha256:595cd56bc11dcb855b6cbca7fbd2b82f44055515dc16f353db7b2d43037c9498` |
| `full-cuda13` | `sha256:f89dfcdccd5d54755fde3e670abd2a29d1ddc83df7aedc27a4bef83c9bffd45d` |

GPU tests used an NVIDIA RTX 3060 12 GB, driver 610.57.04, one explicitly selected
GPU UUID, NVIDIA runtime and `compute,utility` capabilities. CUDA detection,
`libggml-cuda.so` loading and CUDA graph warmup were logged in both CUDA variants.
100 ms GPU sampling during the browser tests recorded 15% peak utilization for
CUDA 12 and 7% for CUDA 13 (total GPU memory peaks 561 and 551 MiB respectively).
These short samples are observations, not a memory cap or comparative benchmark.

## Model download and browser tests

Each variant downloaded `pocket_tts_english_q8_0` through the actual native WebUI
in isolated headless Chrome, using the displayed download confirmation. Each
download completed with exit code 0 and 134051128 downloaded bytes. No personal
voice assets were copied. The package includes the stock Alba embedding.

The browser selected Pocket TTS and an available bundled quick-start demo voice
(`demo_1_man`), ran speech generation and saved the result through **Save WAV**.
Each saved file decoded as mono, 24 kHz, 16-bit PCM:

| Variant | Browser-generated audio duration |
| --- | --- |
| CPU | 4.64 s |
| CUDA 12 | 4.88 s |
| CUDA 13 | 4.64 s |

The browser initially offered only the four demo voices before model loading;
the test did not assume Alba was present in that dropdown. The direct API tests
used the downloaded stock `alba` voice. Browser automation waited for model
inventory readiness and saved the UI's generated blob rather than relying on
the automation driver's empty body capture for a streamed HTTP response.

## Direct API and persistence tests

Every API sample was validated as non-silent 24 kHz mono PCM16 WAV. Requests used
a short fixed sentence with stock voice `alba`. Timings below measure the speech
HTTP request, excluding any separate model-registration/load call.

| Test | WAV bytes | Audio duration | Request wall time |
| --- | ---: | ---: | ---: |
| CPU API | 207404 | 4.32 s | 4.917 s |
| CPU after restart | 218924 | 4.56 s | 5.263 s |
| CUDA 12 API | 222764 | 4.64 s | 0.300 s |
| CUDA 12 after container removal/recreation | 211244 | 4.40 s | 0.763 s |
| CUDA 13 API | 230444 | 4.80 s | 0.237 s |
| CUDA 13 after restart | 211244 | 4.40 s | 0.522 s |

Downloaded model files persisted through lifecycle tests. As expected for the
upstream UI-only launch, `/v1/models` was empty after process restart/container
recreation: dynamic model registrations are not stored as server configuration.
The test registered/loaded the existing model through `/v1/models/load`, then
generated speech successfully without redownloading weights. Stable API model
registration across restarts still requires the documented upstream JSON setup.

## Limits and remaining acceptance work

- This validates one public model package, not gated downloads, Python fallback
  installers or every model. Numeric UID overrides may affect HOME/token/cache
  assumptions in those other paths; they have not been tested.
- NVIDIA access succeeded on this host without extra group flags. Other GPUs,
  drivers and future Vulkan device permissions require separate validation.
- Reverting to the image's default UID 1000 does not make files owned by 99
  writable to it. Preserve the chosen user setting when recreating/updating the
  container; an identity migration is distinct from rolling back image contents.
- Existing unrelated shared directories may have different owners/modes. Do not
  recursively change permissions as part of installation or assume this setting
  fixes every pre-existing storage layout.
- The NVIDIA `driverInitFileInfo ... result=11` startup warnings and legacy model
  metadata warning remain. They did not prevent measured CUDA inference, but
  their appearance is not proof that every similar error is harmless.
- No subjective listening evaluation, CA branch-selector UI test, automatic
  rolling-tag update, image-version rollback, long-running soak, gated-model test,
  or full hardware/model compatibility matrix was completed by this experiment.
- The template now includes the tested identity, but the actual CA installation
  and update paths still need acceptance checks. No container runtime wrapper
  is needed for this approach.

## Cleanup and retained evidence

Only the isolated test container was stopped/removed. The three sets of downloaded
stock test-model files, small harness and official images were retained for
reproducibility; test appdata totals approximately 384 MiB and can be reused for
the remaining tests. All three downloaded model GGUF files have SHA256
`0315406421d515d9ffbde49ed998832ff2962562ef8abde440c85fa0a27d8b2a`. No production
container, appdata, driver or host Docker configuration was changed.

Screenshots, browser automation and validated WAV samples are local test artifacts
under `build/unraid-ca-validation/` in the development workspace, outside this
standalone public repository candidate.
