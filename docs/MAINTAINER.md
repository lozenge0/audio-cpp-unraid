# Maintainer guide

For installation and everyday use, start with the [README](../README.md).
This page collects project scope, validation history, release process and sources
previously in the README. The [release review](RELEASE-REVIEW.md) is the current
status tracker; detailed experiment reports remain in this docs directory.

## Validation and submission context

The current submission state, completed evidence and remaining gates live in
[the release review](RELEASE-REVIEW.md). Do not repeat that status here.

CPU, CUDA 12 and CUDA 13 passed isolated Pocket TTS testing on one
Unraid host. Native Docker `--user=99:100` resolved the initial model-folder
permission failure. The [September 12 CPU retest](CPU-RETEST-20260912.md) passed
short-text, streaming and restart checks on a fixed official image. Controlled
CUDA 13 recreation, image update and rollback passed within their documented
scope. These are not full Community Apps release acceptance, and portal approval
does not establish runtime compatibility.

The repository is `lozenge0/audio-cpp-unraid`, with GitHub Issues for support.
The template requests both **AI** and **Tools** categories.

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
- [Configuration reference](CONFIGURATION.md): detailed deployment and tuning notes.
- `tests/`: maintainer-only structural checks; never shipped into the container.
- `.github/`: read-only CI checks and Dependabot updates for the CI actions only.

The project is called **audio.cpp for Unraid**; the template/container name is
`audio-cpp`. Integration versions (`v0.1.0`, eventually `v1.0.0`) do not represent
the version of upstream audio.cpp running inside the container. This integration
does not imply endorsement by the audio.cpp maintainers or Unraid.

## Maintainer checks and publishing

Run from the repository root (not this docs directory), with Python 3.9+:

```sh
python3 -m unittest discover -s tests -v
```

These checks validate local structural/design invariants, not the CA parser,
live registry availability, hardware, browser workflows, or installation success.
Follow [the release review](RELEASE-REVIEW.md) and
[full acceptance checklist](VALIDATION.md) before any release.

The GitHub Actions workflow runs these tests on pushes, pull requests
and manual dispatch, with no custom secrets, image builds or server access.
Dependabot proposes CI action updates for review, not container updates.
See [contribution guidance](../CONTRIBUTING.md) and
[security reporting](../SECURITY.md).

Next verify catalog visibility and the public branch-selection/install flow,
review tested images and complete or explicitly defer outstanding lifecycle
checks. Rerun CA Validate/Scan after meaningful XML changes. Follow the
[GitHub publishing checklist](PUBLISHING.md). Never publish the surrounding
audio.cpp checkout. Portal approval is not full deployment acceptance.

When a template change affects installed users, add a dated entry to the
`Changes` field in `templates/audio-cpp.xml`. Community Apps shows that field
as the app changelog. Docker Manager does not refresh installed templates, so
the entry must say what an existing user needs to change by hand.

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

The [MIT licence](../LICENSE) applies to this integration's templates, documentation
and tests, not upstream software, third-party dependencies or model weights.
The icon is separately dedicated under CC0 1.0 Universal, to the extent the owner
holds applicable rights; see [artwork provenance and terms](../assets/README.md).
The owner approved these choices and subsequent GitHub draft publication on
2026-09-12.
