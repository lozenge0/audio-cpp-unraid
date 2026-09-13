# Changelog

User-facing changes to the Unraid integration. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Version numbers
describe this integration, not upstream audio.cpp. `v1.0.0` is reserved for a
validated stable integration. Entries that affect installed users are mirrored
in the template's `Changes` field, which Community Apps shows as the app changelog.

## [Unreleased]

Targeting `v0.1.0`, the first beta release.

### Added

- Community Apps template for audio.cpp with CPU, NVIDIA CUDA 12 and NVIDIA
  CUDA 13 variants, using unmodified upstream Docker images.
- Model storage, host port and NVIDIA GPU selection fields.
- A `Changes` field in the template so Community Apps shows release notes.
- A PNG export of the community icon for the Unraid Docker page.
- First-time user guide in the README, with configuration, maintainer and
  validation notes under `docs/`.

### Changed

- New installations default to host port `6969`. Existing installations keep
  their configured port.
- Every variant runs as Docker user `99:100`, which matches the ownership of
  model folders that Unraid creates. No image or file permissions are changed.

### Fixed

- The Unraid Docker page showed no icon because the template pointed at an SVG.
  Docker Manager caches icons as PNG.

### Known limitations

- Public Community Apps branch selection, scheduled container updates and the
  optional JSON configuration path are not yet validated. See the
  [release review](docs/RELEASE-REVIEW.md).
