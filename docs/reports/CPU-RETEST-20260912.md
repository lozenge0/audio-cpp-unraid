# Official CPU image regression retest — 2026-09-12

## Scope and image

Retest Pocket TTS English GGUF Q8 short-text speech on Unraid 7.3.2 with a
Ryzen 7 3700X. The previous official CPU image, revision `b075757`, exited 139
with `GGML_ASSERT(tensor->buffer == NULL)` after the owner's `hello` request.
The original failed container and logs were retained; it was not rerun today.

The official `full-cpu` tag resolved on September 12 to:

- Index: `sha256:3d7f38d657bbc0234825cc3680bc251aa1dea6e941e6e8b7f8d76a76bed27472`
- Linux amd64 image/config ID (not a pullable manifest digest): `sha256:32b6076c70ae1e730ea193ce88b6687f97869681ba5886cb3fb64eefa63e0615`
- Source: `5bea9c726881f6a7ce3e9adf18c060b5a6a8eb8e`
- Image creation: `2026-09-12T08:15:41Z`

The test pins the index digest rather than following the moving tag. This is a
development image, not a claim about the latest numbered release.
An independent subagent confirmed the successful [upstream Docker build](https://github.com/0xShug0/audio.cpp/actions/runs/34682133956)
and ancestry containing [fix 88107a4](https://github.com/0xShug0/audio.cpp/commit/88107a4344778b8befa0aac25cf5b47d0274ca63).
The [maintainer's explanation](https://github.com/0xShug0/audio.cpp/issues/488#issuecomment-5587057112)
identifies duplicate CPU tensor-view initialization in streaming; it does not
claim that all possible short-text failures have been fixed.

## Isolation

A separately named CPU retest container uses a copy of the old test's model
directory, with hashes and ownership checked before deployment. Existing CPU,
CUDA 12 and personal containers/data are preserved. Only the isolated CUDA 13
test was stopped to release the shared test port. No existing container was
deleted or renamed, and no saved Unraid template or updater setting was edited.
The deployment harness and actual image/configuration snapshot were independently
reviewed before creation/start.

The unchanged official application runs with `--user=99:100`, `runc`, no GPU
mapping, no privileged mode, and:

```text
server --ui --ui-management --host 0.0.0.0 --port 8080 --backend cpu
```

The existing GGUF hash is
`0315406421d515d9ffbde49ed998832ff2962562ef8abde440c85fa0a27d8b2a`;
the Alba embedding hash is
`69c32db63ca56843d994f81f343f62e0bf2d73f7e4c9bc73e44bb1110b1d8845`.
No personal voices, configuration, wrapper, model patch or custom image is used.

## Test results

| Path | Cases | Result |
| --- | --- | --- |
| Offline API, Alba | `hello`, longer sentence, `hello` | Pass; valid non-silent 24 kHz mono PCM16 WAV |
| Studio, Alba | `hello`, longer sentence, `hello` | Pass; HTTP 200, captured request and WAV |
| Offline API, previous male demo voice | `hello`, `demo_1_man` | Pass; 0.72-second non-silent WAV |
| Explicit streaming, male demo voice | `hello`, longer sentence, `hello` | Pass; 9 / 63 / 9 audio delta events, completion and non-silent PCM |
| Fresh process after restart | Streaming male `hello` / longer / `hello`, then offline API and Studio Alba `hello` | Pass; model files reused without download |

Offline API Alba durations were 0.64 / 4.16 / 0.56 seconds; Studio durations
were 0.64 / 4.80 / 0.64 seconds. All requests were sequential and followed by
a successful CPU health check. Streaming explicitly registers a model with
`mode: streaming`, then requests `response_format: pcm` and `stream_format: sse`.
The client checks embedded errors, `speech.audio.delta`, `speech.audio.done`
and `[DONE]`; HTTP 200 alone is not counted as a pass. Responses are read to
completion, so this is not a time-to-first-audio or network chunk-timing test.

After restart, streaming was the first inference path exercised; its event counts
and PCM outputs matched the earlier run. Offline and Studio Alba each produced
0.64-second WAVs afterward. Final health was `ok`, backend `cpu`, two registered
models. Dynamic model registrations were explicitly recreated by the test clients;
this is not automatic registration persistence.

Final checks confirmed the original and copied model files, UID/GID and modes
were unchanged. All pre-existing audio.cpp container configurations and saved
Unraid XML files matched the before snapshot. The new pinned CPU retest remains
running on host port 18081; CUDA 13 is retained stopped, and the personal service
and old failed CPU container remain untouched. No files, containers or images
were deleted.

Independent final review verified all nine successful WAVs and six streaming
PCM outputs were non-silent, the before/after model manifests matched, and logs
loaded `libggml-cpu-haswell.so` on both process starts without assertion/crash
errors. CPU portability/model-coverage and legacy GGUF-spec warnings remain.
All 16 local template structural tests passed. These checks do not replace
broader hardware/model acceptance. After the automated tests, the owner opened
the running CPU WebUI and confirmed that it was "working well". This completes
the owner listening check for the sample they tried, not every saved test output.

### Studio voice change

Two initial browser attempts stopped before sending speech because the harness
expected the former male preset. Current upstream Studio prioritizes the model's
declared built-in voices: Pocket TTS exposes Alba. Updating only the private
browser test to select Alba resolved this mismatch. Male demo voices remain
available through the API and were covered there. No application fix was made.
See the pinned [Studio source](https://github.com/0xShug0/audio.cpp/blob/5bea9c726881f6a7ce3e9adf18c060b5a6a8eb8e/webui/native/src/routes/+page.svelte)
and [Pocket TTS model specification](https://github.com/0xShug0/audio.cpp/blob/5bea9c726881f6a7ce3e9adf18c060b5a6a8eb8e/model_specs/pocket_tts.json).

## Interpretation and limits

The tested image passes the previously problematic short input and explicit CPU
streaming cases on this host. This supports using the upstream fix rather than
changing the Unraid integration. It is not a same-day old/new bisect, exact replay
of the original unrecorded request options, or validation of all models/hardware.
Audio is structurally validated and non-silent, with subsequent owner listening
confirmation as described above. Fresh model downloading, full DockerMan
update flow, public CA branch selection and optional JSON remain separate gates.

Private request logs, SSE/PCM/WAV outputs, screenshots, image/configuration
snapshots and model manifests are retained outside the publication directory.
