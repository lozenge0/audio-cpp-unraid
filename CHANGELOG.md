# Changelog

## Unreleased — targeting v0.1.0

- Reworked the README around first-time use, hardware choice, installation and a
  first speech sample. Moved detailed configuration, validation context and
  maintainer notes into linked guides without changing container settings.
- Added AI alongside Tools categorization for the base app and inherited CUDA
  variants. Replaced pre-submission wording after owner-reported CA auto-approval;
  beta status, catalog visibility uncertainty and remaining runtime checks retained.
- Initial draft: one Community Apps template with CPU, CUDA 12 and CUDA 13 variants.
- Direct moving upstream image references; no application builds or runtime wrappers.
- Native model storage, network port and NVIDIA selection fields.
- Native Docker `--user=99:100` for all variants, matching tested Unraid-created
  model-directory ownership without modifying upstream images or file permissions.
- Isolated CPU/CUDA 12/CUDA 13 downloads and browser/API inference, plus
  owner-operated installation of pre-expanded private CA templates.
- Controlled CUDA 13 recreation, newer-image update and retained-container
  rollback with configuration/model integrity checks.
- September 12 fixed official CPU image passed short-text, explicit streaming
  and restart regression tests; owner subsequently confirmed playback.
- Public CA branch selection, full DockerMan/scheduled update workflows and
  optional JSON configuration remain outstanding; no full acceptance claim.
- Reconciled release review and explicit publication file list.
- Upstream artwork-independent community icon supplied by the project owner.
- Owner approved MIT for integration files and CC0 1.0 for the icon on September
  12, limited to rights they hold; upstream licences are unchanged.
- Local structural checks and a deployment acceptance checklist.
- Independent pre-GitHub template/privacy review; removed a host-specific GPU
  prefix from a test fixture, clarified optional JSON validation and image ID labels.
- Local light/dark icon previews and read-only embedded metadata inspection;
  original artwork unchanged.
- Prepared least-privilege, commit-pinned GitHub Actions CI, Dependabot action
  updates, contribution/security guidance and a standalone Git publishing checklist.
- September 13: published the approved GitHub review draft with a clean signed
  history and noreply commit identity. First hosted CI passed all 25 checks;
  public links/file hashes and recorded repository security settings verified.

No public versioned release has been made; the GitHub repository is a review draft.
Version numbers describe the Unraid integration,
not upstream audio.cpp. v1.0.0 is reserved for a validated stable integration.
