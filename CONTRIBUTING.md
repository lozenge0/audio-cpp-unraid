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
   inventory in `scripts/check_publication.py`.
4. If behavior changes, update setup guidance and the changelog. If the change
   affects installed users, add an entry to the template's `Changes` field.
   Record runtime tests in a dated report under `docs/reports/`. CI has no
   Unraid server or GPU.

Before committing, configure this checkout to use your **public GitHub handle**
as `user.name` and the matching GitHub noreply address as `user.email`. Copy the
address from your GitHub email settings; do not use a personal mailbox. Both
the name and email are published in commits, including merges and tags.
Use repository-local settings, leaving other projects unchanged:

```sh
git config --local user.name PUBLIC_HANDLE
git config --local user.email YOUR_GITHUB_NOREPLY_ADDRESS
git config --local user.useConfigOnly true
git config --local core.hooksPath .githooks
```

Replace the uppercase placeholders with your own public identity. If you already
use custom Git hooks, integrate these checks with them before changing hooksPath.
Hooks are not activated automatically by cloning the repository.

The hooks check the staged snapshot, commit message and every outgoing commit
before a push. Tests receive the same content checks as other files. A file
removed in a later commit can still block publication because its earlier
contents would be uploaded. The push hook queries the actual destination's
advertised branch tips and excludes history already reachable there, including
when creating a branch. It does not trust local remote-tracking refs. An empty
destination requires checking from the root; annotated tags also have their
messages and tagger identities checked. Shallow clones must fetch complete
history before these checks can pass. If the destination cannot be queried,
the push is blocked.
Diagnostics omit matched values and unapproved filenames. Do not bypass a failed
check or paste raw Git output into a public issue.

GitHub's browser can create commits/merges with a different author name from
your local configuration. Until that identity has been verified to use your
public handle, create commits and merges locally with these hooks enabled.
CI provides a second check after upload; it cannot prevent an initial leak.

Public reports should retain test versions, relevant hardware, image/model
digests, methods, results and limitations. Omit personal service inventories,
storage availability, private artifact locations, operational schedules and
unnecessary server state. Privacy amendments to dated reports must be labelled
without changing their original test conclusions. Do not upload raw audio,
screenshots or logs as evidence by default.

Pull requests run read-only CI on GitHub-hosted runners. Passing CI does not prove
hardware compatibility or CA acceptance. Action updates are proposed by Dependabot
and need maintainer review; they are not automatically merged. Do not replace
commit-pinned actions with unpinned tags without a deliberate security review.

Contributed integration files use the root [MIT licence](LICENSE). Artwork has
[separate CC0 terms](assets/README.md); disclose the provenance and applicable
rights of any proposed asset. Do not alter preserved provenance metadata silently.
