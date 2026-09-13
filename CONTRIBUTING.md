# Contributing

This repository packages the Unraid integration, not audio.cpp itself. Keep
application images upstream-owned and unmodified. Do not add runtime wrappers,
custom image builds, bundled models/voices or personal configuration defaults.

For an installation issue, include the Unraid version, selected CPU/CUDA variant,
official image tag and digest, relevant hardware/driver versions, steps to
reproduce and a short sanitized error excerpt. Remove credentials, private
addresses, GPU UUIDs, personal paths and private text/audio. Do not attach full
Docker inspections or server configuration dumps. See [security reporting](SECURITY.md)
for sensitive issues. Application bugs may belong upstream, but check that the
failure is not caused by template settings before redirecting a report.

Before proposing a change:

1. Explain its purpose and keep changes scoped to the integration.
2. Run `python3 -m unittest discover -s tests -v` from the repository root.
3. If adding a file, review its publication safety and add it to the explicit
   inventory in `tests/test_publication.py`.
4. If behavior changes, update setup guidance and the changelog. If the change
   affects installed users, add an entry to the template's `Changes` field.
   Record runtime tests in a dated report under `docs/reports/`. CI has no
   Unraid server or GPU.

Pull requests run read-only CI on GitHub-hosted runners. Passing CI does not prove
hardware compatibility or CA acceptance. Action updates are proposed by Dependabot
and need maintainer review; they are not automatically merged. Do not replace
commit-pinned actions with unpinned tags without a deliberate security review.

Contributed integration files use the root [MIT licence](LICENSE). Artwork has
[separate CC0 terms](assets/README.md); disclose the provenance and applicable
rights of any proposed asset. Do not alter preserved provenance metadata silently.
