# audio.cpp for Unraid

Run audio AI models on your own Unraid server, with a browser interface for
trying them and an API for connecting your own applications.

This community app installs the **official, unmodified audio.cpp Docker image**
and enables its built-in WebUI. You do not need to compile anything or write
code to get started. A model is a downloadable AI package for a particular task,
such as speech generation or transcription. Choose the models you want after installation;
this template does not select a model, bundle extra voices, or add custom
application code.

**Beta integration:** basic speech generation has been tested on CPU and NVIDIA
GPU setups, but public-listing installation checks are still in progress.
See [tested hardware and known limitations](docs/RELEASE-REVIEW.md).

## What can I use it for?

Depending on the model you choose, upstream audio.cpp can:

- **Turn text into speech:** create narration, spoken messages or voiceovers.
- **Transcribe recordings:** turn speech in an audio file into text.
- **Work with existing audio:** use supported models for tasks such as voice
  conversion or separating vocals from music.
- **Generate music or sound effects:** experiment with models that support those tasks.

These are upstream capabilities, not a promise that every model works on every
device. Our Unraid testing so far focuses on **Pocket TTS English GGUF Q8**.
Check [upstream's supported models](https://github.com/0xShug0/audio.cpp#supported-models)
for each model's features and requirements. Use recordings and voices you have
permission to use.

The server runs the models locally. You still need internet access to pull the
Docker image and download model packages; review each model's licence before use.

## Choose your hardware option

| Option | When to choose it |
| --- | --- |
| **CPU** | You do not have a compatible NVIDIA GPU, or want the simplest setup. Performance depends on your CPU and model. |
| **NVIDIA / CUDA 12** | You have an NVIDIA GPU with a compatible driver and the Unraid NVIDIA Driver plugin installed. |
| **NVIDIA / CUDA 13** | Your GPU and driver support the CUDA 13 image. Do not select it just because its version number is higher. |

An AMD or Intel **CPU** can use the CPU option if supported by the upstream image.
AMD/Intel **GPU acceleration** is not offered by this template yet. NVIDIA
acceleration needs enough free GPU memory for your chosen model; other containers
sharing the GPU also consume that memory.

For image tags, driver considerations and GPU selection details, see the
[hardware reference](docs/CONFIGURATION.md#hardware-variants).

## Install on Unraid

Before starting, have space for both the Docker image and downloaded models,
and enough RAM (or GPU memory) for the model you intend to run.

1. In Unraid's **Apps** tab, search for `audio-cpp` and select the entry maintained
   by `lozenge0`. If it is not visible, check the [listing status](docs/RELEASE-REVIEW.md);
   do not confuse a private test entry with the public app.
2. Choose CPU, CUDA 12 or CUDA 13. **Do not switch hardware support by changing
   only the image tag**—the NVIDIA options also need GPU runtime settings.
3. Review **WebUI / API port**. Keep host port `6969` if it is free; otherwise
   choose an unused host port. Leave the container port at `8080`.
4. Review **Model storage**. The suggested folder is
   `/mnt/user/appdata/audio-cpp/models`. It stores downloaded models so they can
   survive container replacement. For a first installation, use a new dedicated
   folder and keep the supplied permission settings.
5. For NVIDIA, review **NVIDIA GPU selection**. The default `all` exposes all
   NVIDIA GPUs; use a specific GPU UUID if you want to limit access to one card.
6. Apply the settings, wait for the image to download and the container to start,
   then open **WebUI** from its menu on Unraid's **Docker** tab.

If you already run audio.cpp, use a **different container name, unused host port
and separate model folder** for this installation. Do not overwrite your working
setup. The `6969` default applies to new installations; existing installations
keep their configured host port.

## Make your first speech sample

The WebUI includes model downloads and a **Studio** for trying models. Names and
layout can change as upstream releases new images.

1. Open the model catalog/download area and choose a text-to-speech model.
   **Pocket TTS English GGUF Q8** is an example we have tested, not a required
   default. “GGUF Q8” identifies the model package/precision.
2. Download it into the mounted models location, `/app/models`, and wait for
   installation to finish.
3. In **Studio**, choose text-to-speech, select the installed model and a voice
   it offers, then generate a short sentence such as:
   “Hello, this is my first audio.cpp test.”
4. Play the result. The first request may take longer while the model loads.
   Try a longer sentence once that works.

No model is preselected by this integration. Different models offer different
voices, languages and controls. A retained download does not necessarily mean
the model is automatically registered after a restart; you may need to select
it again. Stable API model IDs need [advanced configuration](docs/CONFIGURATION.md#optional-advanced-configuration).

## Use it from another application

You can also use audio.cpp as an audio-processing service for your own scripts
or apps—for example, to generate spoken notifications or transcribe recordings.
Those integrations are yours to configure; this template does not add them.

Use your Unraid server's address and the **host port** you selected. The server
provides `/health` for a server-health check and `/v1/models` to list registered
model IDs. A healthy server does not prove a model is loaded or ready to generate.
Use the registered IDs, not guessed model names, when making requests.

See the [official API guide](https://github.com/0xShug0/audio.cpp/blob/main/app/server/README.md)
for speech generation, transcription and other endpoints. Some endpoints use
OpenAI-style formats; that does not guarantee compatibility with every client.

## Security

**There is no login or API authentication in this setup.** Anyone who can reach
the port may be able to run jobs and manage models. Keep it on a trusted network;
do not expose the port directly to the internet. Remote access needs separate,
authenticated protection. See [security guidance](SECURITY.md).

## Storage and updates

Keep your model folder and any configuration backed up. The template runs as
`99:100`, the numeric user/group used for new model folders on the tested Unraid
host. Leave that setting in place; do not add `PUID`/`PGID` variables or broadly
change appdata permissions to fix an error.

Container updates come directly from upstream's rolling images, not only numbered
releases. This template does not enable automatic updates for you. Test your
setup before enabling them and retain a known-good image reference for rollback.
An image update does not update your models or GPU driver.

See [permissions](docs/CONFIGURATION.md#storage-permissions-and-process-identity)
and [updates/rollback](docs/CONFIGURATION.md#updates-persistence-and-rollback)
for the details.

## Need help?

- **WebUI will not open:** check that the container is running, its logs, and the
  host port you selected.
- **A download fails:** check free space and model-folder permissions.
- **Generation fails or says “Failed to fetch”:** check container logs and whether
  it stopped; the message alone does not identify the cause. Note the model and
  image version when reporting it.
- **Installation/template questions:** open an issue in
  [lozenge0/audio-cpp-unraid](https://github.com/lozenge0/audio-cpp-unraid/issues).
  Remove credentials, private paths and personal text/audio from reports.

## Further reading

- [Configuration reference](docs/CONFIGURATION.md): image variants, permissions,
  tuning, optional JSON and rollback.
- [Tested images and remaining checks](docs/RELEASE-REVIEW.md): what we have and
  have not verified.
- [Maintainer guide](docs/MAINTAINER.md): project scope, CI, release process and
  links to detailed test reports.
- [Upstream audio.cpp](https://github.com/0xShug0/audio.cpp): model capabilities,
  software documentation and development.

The integration is community-maintained, not an official endorsement by audio.cpp
or Unraid. Its files use the [MIT licence](LICENSE), not the licences of upstream
software or model weights. The icon is separately dedicated under CC0 1.0 to the
extent the owner holds applicable rights; see [artwork terms](assets/README.md).
