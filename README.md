# audio.cpp for Unraid

Community-maintained Unraid templates using **unmodified upstream audio.cpp
Docker images** and the upstream WebUI. No fork, custom image, startup wrapper,
bundled model, voice recording, or generated server configuration.

**Status: beta integration, targeting v0.1.0; full deployment acceptance pending.**
CPU, CUDA 12 and CUDA 13 have passed isolated Pocket TTS testing on one Unraid
host. Native Docker `--user=99:100` resolved the initial model-folder permission
failure. The [September 12 CPU retest](docs/CPU-RETEST-20260912.md) passed short-text,
streaming and restart checks using a fixed official image; the owner also confirmed
playback. Controlled CUDA 13 recreation, image update and rollback passed within
their documented scope. These are not full Community Apps release acceptance.
See the [current release review](docs/RELEASE-REVIEW.md) for completed checks,
remaining gates and the exact proposed repository contents.
The selected repository destination is `lozenge0/audio-cpp-unraid`, with GitHub
Issues as the integration support destination. The owner reports completing the
Community Apps submission and receiving automatic approval. Catalog visibility
and installation through the public listing are not yet verified. Portal approval
does not establish runtime compatibility. See the release review for current status.

The template requests both **AI** and **Tools** categories. Catalog placement
depends on CA processing the updated template; it has not yet been confirmed live.

## Scope and layout

This is a standalone integration repository with its own clean Git history.
It was prepared separately from the upstream audio.cpp source; no upstream
checkout/history belongs here. Do not build an application image from this
repository. Nothing here changes an existing personal installation.

- `templates/audio-cpp.xml`: one app with CPU base and two CUDA branches.
- `ca_profile.xml`: Community Apps repository metadata.
- `assets/`: supplied community integration icon and provenance/licensing notes.
- `docs/PLAN.md`: implementation stages and approval boundaries.
- `docs/VALIDATION.md`: acceptance checklist and evidence requirements.
- `docs/RELEASE-REVIEW.md`: current release status and publication boundaries.
- `tests/`: maintainer-only structural checks; never shipped into the container.
- `.github/`: read-only CI checks and Dependabot updates for the CI actions only.

The project is called **audio.cpp for Unraid**; the template/container name is
`audio-cpp`. Integration versions (`v0.1.0`, eventually `v1.0.0`) do not represent
the version of upstream audio.cpp running inside the container. This integration
does not imply endorsement by the audio.cpp maintainers or Unraid.

## Hardware variants

| Selection | Direct upstream image | Required host support |
| --- | --- | --- |
| CPU (base) | `ghcr.io/0xshug0/audio.cpp:full-cpu` | Supported CPU; no GPU runtime |
| NVIDIA / CUDA 12 | `ghcr.io/0xshug0/audio.cpp:full-cuda12` | Compatible NVIDIA GPU, driver and NVIDIA runtime |
| NVIDIA / CUDA 13 | `ghcr.io/0xshug0/audio.cpp:full-cuda13` | CUDA 13-compatible GPU, driver and NVIDIA runtime |

None of these variants has passed full deployment acceptance yet. The native
user/group override now included in the draft passed isolated downloads and
browser/API inference with all three images on one Unraid 7.3.2 host; both CUDA
variants used an RTX 3060 12 GB. See the exact digests and limitations in the
[current validation summary](docs/VALIDATION.md). The older CPU image in the
initial identity tests subsequently failed short text; use the fixed-image
retest record when assessing CPU support.
Earlier personal CUDA 12 testing is not a substitute for a fresh installation.
CUDA 13 excludes pre-Turing architectures; CUDA version alone does not prove
that a particular card, driver, image and model combination works.

Vulkan and HIP/ROCm are not offered by this draft. Upstream's
[reviewed Docker workflow](https://github.com/0xShug0/audio.cpp/blob/5bea9c726881f6a7ce3e9adf18c060b5a6a8eb8e/.github/workflows/docker.yml)
now includes `full-vulkan`; the earlier statement that upstream only built the
three images above is outdated. A Vulkan branch still needs its own device,
permission and hardware validation. No Vulkan or HIP/ROCm support is claimed here,
and no additional branch or startup compilation has been added.

Community Apps expands branches into installation configurations. A branch can
replace launch arguments, Docker parameters and the **entire** Config list.
This is an install/reinstall selector, not a reactive hardware dropdown in
Docker Edit. Do not switch CPU to CUDA by changing only the image tag.

## Initial setup (proposed; acceptance pending)

For testing alongside an existing installation, first choose a **different
container name, unused host port and fresh storage directory**. The template's
`audio-cpp` name could otherwise collide with an existing personal container.

1. Choose the hardware variant. NVIDIA hosts need the NVIDIA Driver plugin,
   a compatible driver and registered NVIDIA container runtime beforehand.
2. Choose a free **host** HTTP port. Suggested port: `8080`; container port stays
   `8080`. The template uses bridge networking and binds the server to
   `0.0.0.0` inside the container so Docker forwarding works.
3. Choose persistent model storage. Suggested host directory:
   `/mnt/user/appdata/audio-cpp/models`, mounted at upstream's `/app/models`.
   For a fresh installation, let Unraid create a new dedicated directory. It
   must be writable by UID `99` / GID `100`; see the permissions guidance below.
4. For NVIDIA, review **NVIDIA GPU selection**. `all` preserves the NVIDIA base
   image's default visibility. Prefer a specific GPU UUID on multi-GPU systems;
   find it with `nvidia-smi -L` on the host. Driver capabilities are
   `compute,utility`. Exposing several GPUs is not distributed inference.
5. Start the container and open WebUI. Select/download models through upstream's
   own interface; no model or voice is forced by the template. Review the chosen
   model's licence, size and backend support before downloading.
6. Verify inference and persistence before enabling Unraid autostart or updates.

### Storage permissions and process identity

All variants set Docker **Extra Parameters** to include `--user=99:100`. This
runs the unchanged upstream application as numeric user `99` and group `100`,
matching the owner/group of new model directories created by DockerMan on the
tested Unraid host (mode `0755`). It overrides the tested images' default
`1000:1000` process identity; it does not modify the images or change file owners.
The image does not implement `PUID`/`PGID`, so adding those variables will not
configure permissions.

Existing or shared storage may have different owners, modes or ACLs. Verify
that UID `99` / GID `100` can traverse and write the selected model directory
before reusing it. This setting does not migrate an existing installation's
permissions. Do not recursively change shared appdata ownership/permissions or
run as root to work around a failure; review the specific directory first.

Keep `--user=99:100` when editing Extra Parameters, recreating the container,
updating or rolling back images. NVIDIA variants additionally require
`--runtime=nvidia`. Numeric UID overrides do not create a home directory or
guarantee access to image-owned cache/token paths. Native Pocket TTS downloads
and inference passed; gated downloads, Python fallback installers and other
HOME-dependent paths still require validation. NVIDIA access needed no extra
groups on the tested host, which does not establish compatibility for all hosts.

Use `/app/models` in the WebUI. Downloading outside a persistent mount can lose
data when the container is replaced. Downloaded files surviving a restart is
separate from dynamic model registrations being restored. For stable API model
IDs after restarts, use upstream's configuration mechanism. Browser-saved voices
are not automatically server-side backups.

## Optional advanced configuration

Leave application tuning unspecified to inherit upstream defaults. Unraid's
**Post Arguments** field contains the server command. Append only documented
upstream options there; Docker **Extra Parameters** is for Docker options, not
audio.cpp flags. Changes take effect after applying/recreating the container.

| Upstream argument | Purpose |
| --- | --- |
| `--device N` | Backend index among devices visible inside the container |
| `--threads N` | Inference CPU threads, not CPU pinning |
| `--max-loaded-models N` | Limit resident models; upstream `0` disables limit |
| `--idle-unload-ms N` | Idle unload timeout in milliseconds; `0` disables |
| `--min-free-memory-mb N` | Estimated host/GPU free-memory margin; `0` disables |
| `--busy-timeout-ms N` | Timeout waiting for a busy model; `0` disables |

The upstream build inspected defaults to device `0`, threads `1`, unlimited
resident models, idle unloading and memory guard disabled, and a busy timeout
of `300000` ms. Defaults can change with rolling images: check the image's
`server --help` and upstream documentation. No personal tuning is baked in here.

If only one GPU is exposed, it is normally device `0` inside the container even
if its host index differs. The memory guard estimates a load's footprint; it is
not a hard VRAM cap, reservation, or protection against another process allocating
memory. CPU pinning and Docker host-RAM limits are separate Unraid/Docker controls.

The following optional JSON recipe has not yet been integration-tested under
UID 99:100 for stable model IDs, restart restoration and CLI precedence. It is
advanced upstream guidance, not a validated setup path for this integration.

For a config-driven deployment, add a read-only host-directory mapping to
`/config`, create **your own** valid upstream `server.json` there, and add
`--config /config/server.json` to Post Arguments. No file is generated or bundled
by this project. CLI arguments override matching JSON settings; the branch's
explicit host/port/backend/UI arguments still apply unless deliberately edited.
The mounted configuration and voice files must be readable, and their parent
directories traversable, by UID `99` / GID `100`.
Use upstream documentation for model IDs, voices, lazy loading and request limits.
An optional voice directory requires a persistent mount and upstream JSON
`voice_dir` configuration or the `--voice-dir` argument; no personal voice data
is included here.

Do not create invented `AUDIOCPP_THREADS` or similar environment variables:
upstream does not map them to these arguments. Do not insert `$VARIABLE` into
ordinary Post Arguments expecting container environment expansion. Separate
friendly tuning inputs would require upstream support; this project does not
add a shell wrapper to implement them.

## Security

This setup provides **no authentication**. The WebUI's management endpoints can
download/delete models and use storage accessible to the container. Keep the
published port on trusted networks; do not port-forward it to the internet.
For access beyond trusted networks, arrange authenticated access separately.
CORS is not authentication; no permissive CORS override is added here.

The template does not request privileged mode, mount the Docker socket, expose
host system directories, install drivers, or change the host Docker daemon.
Mount only the data needed. GPU runtime access is limited to the chosen variant.

## Updates, persistence and rollback

The template references moving upstream tags, **not pinned digests**. Upstream
currently publishes rolling Docker builds when new commits are available; these
are not exclusively numbered releases. With a user-enabled Unraid container
updater, the user's chosen tag is checked/pulled on their schedule and the
container is recreated. We run no image-building or image-mirroring pipeline.

Updates remain on the selected CPU/CUDA tag; they do not switch backend, upgrade
host drivers, update model weights, or safely migrate every installation setting.
Template changes are not a universal migration mechanism for installed containers.
An existing installation is not automatically migrated to UID `99` / GID `100`
by this template change. Review its current identity and storage before adopting
the setting; preserve the matching identity throughout an image update/rollback.
Moving tags can include regressions or changed driver requirements. Users choose
whether to enable automatic updates; the template does not enable them for users.

Before enabling unattended updates, retain the working image digest/reference,
container settings and a backup of persistent data. Test replacing the container
and reusing model storage. For rollback, disable updates, restore the known-good
image reference (and compatible backed-up configuration/data if necessary), then
recreate only this container. Rolling back an image cannot undo model/data changes.
An upstream dated tag or digest can be used to opt out of rolling image updates.

## Maintainer checks and publishing

Run from this directory, with Python 3.9+:

```sh
python3 -m unittest discover -s tests -v
```

These checks validate local structural/design invariants, not the CA parser,
live registry availability, hardware, browser workflows, or installation success.
Follow [the release review](docs/RELEASE-REVIEW.md) and
[full acceptance checklist](docs/VALIDATION.md) before any release.

The GitHub Actions workflow runs these tests on pushes, pull requests
and manual dispatch, with no custom secrets, image builds or server access.
Dependabot proposes CI action updates for review, not container updates.
The [first hosted run](https://github.com/lozenge0/audio-cpp-unraid/actions/runs/34725657862)
passed all 25 checks. See [contribution guidance](CONTRIBUTING.md) and
[security reporting](SECURITY.md).

The public repository and hosted CI are verified, and the owner reports CA
auto-approval. Next verify catalog visibility and the public branch-selection/install
flow, review tested images and complete or explicitly defer outstanding lifecycle
checks. Rerun CA Validate/Scan after meaningful XML changes. Follow the
[GitHub publishing checklist](docs/PUBLISHING.md). Never publish the surrounding
audio.cpp checkout. Portal approval is not full deployment acceptance.

## Primary references

- [Upstream Docker guide](https://github.com/0xShug0/audio.cpp/blob/main/docs/docker.md)
- [Upstream Docker publishing workflow](https://github.com/0xShug0/audio.cpp/blob/main/.github/workflows/docker.yml)
- [Upstream server guide](https://github.com/0xShug0/audio.cpp/blob/main/app/server/README.md)
- [CA starter repository](https://github.com/unraid/unraid-community-apps-starter)
- [CA submission requirements](https://ca.unraid.net/submit/help)
- [CA XML fields](https://ca.unraid.net/submit/help/xml-field-reference)
- [Unraid container settings](https://docs.unraid.net/unraid-os/using-unraid-to/run-docker-containers/managing-and-customizing-containers/)
- [NVIDIA container GPU selection](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/docker-specialized.html)
- [CUDA 13 compatibility changes](https://docs.nvidia.com/cuda/archive/13.0.0/cuda-toolkit-release-notes/index.html)

## Licensing

The [MIT licence](LICENSE) applies to this integration's templates, documentation
and tests, not upstream software, third-party dependencies or model weights.
The icon is separately dedicated under CC0 1.0 Universal, to the extent the owner
holds applicable rights; see [artwork provenance and terms](assets/README.md).
The owner approved these choices and subsequent GitHub draft publication on
2026-09-12. The owner subsequently completed the CA submission and reported
auto-approval. No versioned integration release has been created.
