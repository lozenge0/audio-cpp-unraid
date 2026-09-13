# Configuration reference

Start with the [first-time setup guide](../README.md). This reference preserves
advanced deployment notes; it does not add settings to the template. Tested
images and open acceptance checks are recorded in [the release review](RELEASE-REVIEW.md).

## Hardware variants

| Selection | Direct upstream image | Required host support |
| --- | --- | --- |
| CPU (base) | `ghcr.io/0xshug0/audio.cpp:full-cpu` | Supported CPU; no GPU runtime |
| NVIDIA / CUDA 12 | `ghcr.io/0xshug0/audio.cpp:full-cuda12` | Compatible NVIDIA GPU, driver and NVIDIA runtime |
| NVIDIA / CUDA 13 | `ghcr.io/0xshug0/audio.cpp:full-cuda13` | CUDA 13-compatible GPU, driver and NVIDIA runtime |
| AMD / Intel — Vulkan | `ghcr.io/0xshug0/audio.cpp:full-vulkan` | AMD or Intel GPU with its kernel driver loaded and `/dev/dri` present |

None of these variants has passed full deployment acceptance yet. The native
user/group override now included in the draft passed isolated downloads and
browser/API inference with all three images on one Unraid 7.3.2 host; both CUDA
variants used an RTX 3060 12 GB. See the exact digests and limitations in the
[current validation summary](VALIDATION.md). The older CPU image in the
initial identity tests subsequently failed short text; use the fixed-image
retest record when assessing CPU support.
Earlier personal CUDA 12 testing is not a substitute for a fresh installation.
CUDA 13 excludes pre-Turing architectures; CUDA version alone does not prove
that a particular card, driver, image and model combination works.

### Vulkan variant

The Vulkan branch was added on 2026-09-13 without a hardware test. The owner
chose to publish it and collect the first report from a volunteer installation.
It uses the upstream `full-vulkan` image, an Ubuntu image with `libvulkan1` and
`mesa-vulkan-drivers`. Mesa supplies the AMD (RADV) and Intel (ANV) Vulkan
drivers, so those GPUs need nothing inside the container. Mesa has no NVIDIA
driver, so NVIDIA users must choose a CUDA variant. HIP/ROCm is not offered.

The branch passes the host directory `/dev/dri` as a Docker device and starts
the server with `--backend vulkan`. Upstream's documented command adds the host
`render` and `video` groups. Unraid has no `render` group. Its `/dev/dri`
nodes belong to `root:video` with mode `660` unless a plugin changes them. The
branch therefore sets Extra Parameters to `--user=99:100 --group-add=18`. `18`
is the numeric id of the Unraid `video` group, inherited from Slackware. The
Intel GPU TOP and Radeon TOP plugins by ich777 load the kernel module. They
also run `chmod -R 777 /dev/dri`, which makes the group irrelevant on those
hosts. The kernel driver must be loaded on the host either way. The image
cannot load it.

Mesa also installs `llvmpipe`, a Vulkan device that runs on the CPU. If the
container cannot open the GPU, the ggml Vulkan backend can still start on that
device and speech works slowly. Use upstream's device listing to confirm which
device is in use:

```sh
docker exec audio-cpp /app/entrypoint.sh server --backend vulkan --list-devices
```

The output lists one device per line, for example
`Vulkan:0 "AMD Radeon RX 6600 (RADV NAVI23)" [gpu]`. A `[cpu]` device type or
`No devices found` means the GPU is not reachable. `/health` reports
`"backend":"vulkan"` but not the device. Upstream's `--device <index>` argument
selects among several Vulkan devices. The template leaves it unset.

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
2. Choose a free **host** HTTP port. Suggested port: `6969`; container port stays
   `8080`. The template uses bridge networking and binds the server to
   `0.0.0.0` inside the container so Docker forwarding works. Existing installations
   keep their configured host port. The WebUI placeholder `[PORT:8080]` refers to
   the container port and resolves to the chosen host port; leave it unchanged.
3. Choose persistent model storage. Suggested host directory:
   `/mnt/user/appdata/audio-cpp/models`, mounted at upstream's `/app/models`.
   For a fresh installation, let Unraid create a new dedicated directory. It
   must be writable by UID `99` / GID `100`; see the permissions guidance below.
4. For NVIDIA, review **NVIDIA GPU selection**. `all` preserves the NVIDIA base
   image's default visibility. Prefer a specific GPU UUID on multi-GPU systems;
   find it with `nvidia-smi -L` on the host. Driver capabilities are
   `compute,utility`. Exposing several GPUs is not distributed inference.
   For Vulkan, keep **GPU device** at `/dev/dri`. Pass a single render node
   such as `/dev/dri/renderD128` only if you know which node belongs to the
   intended GPU.
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
`--runtime=nvidia`. The Vulkan variant additionally requires `--group-add=18`
so that UID 99 can open the `/dev/dri` nodes owned by the `video` group. Numeric UID overrides do not create a home directory or
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
The README section [Already installed?](../README.md#already-installed) lists
the template changes that an existing installation can adopt by hand.
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
