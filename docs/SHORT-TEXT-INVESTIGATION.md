# Short-text CPU crash: investigation plan

Prepared 2026-09-08. Follow-up: [official CPU image retest](CPU-RETEST-20260912.md)
records the September 12 results. The historical plan below is not a claim that
every proposed comparison was executed. Execution and
any test-container lifecycle changes follow owner approval of this plan.

## Question and existing evidence

Determine whether the short-text failure is caused by an upstream decoder bug,
an image/build difference, process identity, request mode, or integration settings.

- Owner reports `hello` with the default male Studio voice crashes the new CPU
  installation, while longer text works. The original CUDA installation handles
  short text, but differs in image revision, backend, identity and configuration.
- The inspected CPU crash used upstream revision
  `b0757573c90bf3ada5cf8ffbc69f3ab80a7a6947`, exit 139, `OOMKilled=false`, with
  `GGML_ASSERT(tensor->buffer == NULL)` at `ggml-backend.cpp:1982`.
- Model/Alba hashes matched earlier successful tests. Required CPU instruction
  flags were present on the Ryzen 7 3700X. There is no evidence of a corrupt
  download or unsupported instruction set causing this assertion.
- Independent source review found a possible repeated initialization of decoder
  tensor views for small frame counts. This remains a hypothesis until the
  failing call path is established. Word count is not an exact audio-length
  threshold, and equal seeds need not produce equal lengths across backends.

## Isolation rules

Use one isolated test container at a time, port 18081, and dedicated test storage.
Recheck current server state before starting; do not assume yesterday's state.
Never stop, start, edit or reuse the personal container's configuration/data.
Check full container identity and mappings before every lifecycle operation.
Preserve logs before restarting a crashed test. Do not enable test autostart or
invoke the global updater. Pinned digests prevent image drift, not necessarily
scheduled container recreation; record IDs/start times to detect interference.
Schedule controlled runs away from the updater window without changing it.

Use unmodified official images. No application patches, startup wrappers,
privileged mode or broad permission changes. New test-only storage copies may
be prepared for identity controls; never change ownership of existing storage.
Leave public template defaults unchanged during diagnosis. Stop once evidence
supports a minimal reproduction; avoid an exhaustive cross-product of tests.

## 1. Capture the actual request

Capture the Studio model-loading and speech requests using an isolated browser
session or an owner-provided, narrowly scoped Network capture. Do not export an
entire browsing session or authentication data. Record text, exact voice ID,
bundled voice/reference asset hash, seed, token limit, options and streaming mode,
including omitted fields that inherit defaults. Do not substitute Alba for the
default male voice. Confirm the expected `demo_1_man` ID from the request itself.

Replay the same request and required setup directly against the isolated API.
If API replay crashes identically, the browser is not necessary to trigger it.
If only Studio fails, compare request sequencing, cancellation and overlap before
blaming Brave or changing the inference backend. Distinguish HTTP response
streaming from an application-level incremental audio-generation setting.

## 2. Establish a repeatable CPU baseline

Use the already tested CPU digest from USER-IDENTITY-TESTS.md, verified as revision
`b075757`. Keep UID/GID 99:100 and all captured request settings constant.

| Case | Process state | Text |
| --- | --- | --- |
| A | Fresh process and identical model registration | `hello` |
| B | Fresh process and identical model registration | `This is an isolated audio server test. Model downloads and speech generation are working.` |
| C | Fresh process, then two sequential requests without restart | The longer sentence, followed by `hello` |

Repeat A and B three times each; repeat C if it reveals different behavior.
Use one request at a time. A healthy server before inference is not a pass.
After every request check process state and health, and validate successful
audio as non-silent decodable WAV with measured duration. Retain crash logs,
exit status and Docker OOM state. Do not repeatedly hammer an exited server.

## 3. Compare backend and image build

Run the same request cases using the official CUDA 12 image at the same upstream
revision, pinned to its recorded digest. Keep model/voice assets, UID/GID and
request settings unchanged; verify CUDA is actually used. CUDA 13 is optional
follow-up, not needed for the first distinction.

If CPU fails and CUDA succeeds, this narrows the issue to a backend or image-build
difference; it does not alone prove the root cause. If supported by that image,
force the CPU backend inside the same CUDA 12 image for an additional control:

- CPU fails in both images, CUDA succeeds: stronger evidence of a CPU code path.
- CPU fails only in the CPU image: investigate packaged libraries/build flags.

Record actual generated frame counts if existing diagnostics expose them. Do
not claim equivalent decoder workloads from identical text/seed alone.

## 4. Target the remaining uncertainty

Only run the controls needed after the baseline/backend results:

- **Process identity:** same failing image and request, using its inspected
  default user instead of 99:100, with byte-identical model/voice copies in
  separate appropriately owned test storage. Ensure access checks pass first.
  An identical assertion under both identities rules out the override as a
  necessary trigger. If only 99:100 fails, investigate permissions/HOME/cache
  differences before classifying it as purely upstream.
- **Streaming:** if the captured request uses a supported incremental mode,
  compare it with non-streaming while changing no other request field. Capture
  outputs/status correctly for each transport rather than treating streamed
  responses as ordinary WAV files.
- **Version:** compare an available older official CPU image using the same
  failing request and controls. Then, if useful, check a newer official CPU
  image. Resolve and record actual revisions/digests before running them; do not
  assume dated tags exist or an older personal CUDA build is a good CPU baseline.
  The suspected code already exists in the earlier local source revision.
  A CPU good/bad pair establishes a regression interval, not an introducing commit.

## 5. Decision and handoff

For every run retain image digest/revision, backend library, effective user,
container ID, model/voice hashes, full test request, request order, timing,
audio duration or failure signature, and post-request process/health status.

Have a subagent independently review the results and reproduction instructions.
Report what is established separately from what remains inferred. Prepare an
upstream issue draft only if the evidence supports it; posting requires explicit
owner approval. Do not modify the public image or claim a fix from a longer-text
workaround. CPU release acceptance remains blocked until a supported official
image passes the reproducer and the normal acceptance tests.

This plan does not include patch development, a source bisect, debugger/core-dump
deployment, global updater changes, or publication. Those are separate follow-ups
if the controlled official-image tests cannot isolate the problem sufficiently.
