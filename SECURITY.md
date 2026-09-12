# Security

This integration is a draft, with no supported public release yet. Once released,
maintenance will focus on the current integration template; it does not provide
security maintenance for upstream images, dependencies, models or Unraid itself.

The application port exposes unauthenticated UI/API management. Keep it on trusted
networks and do not expose it directly to the internet. Model storage permissions
and GPU access are described in the [README](README.md#security).

Do not post credentials, private audio or exploitable vulnerability details in
public issues. Use the repository's
**Security → Advisories → Report a vulnerability** option for sensitive integration
reports. Private vulnerability reporting was enabled and verified through
GitHub's API on September 13, 2026; the advisories page is live. See the
[publication checklist](docs/PUBLISHING.md).
If it is unavailable, request a private reporting channel in a public issue
without including sensitive details. Follow upstream's own reporting policy for
vulnerabilities in audio.cpp; do not assume this integration can fix them.

No response-time guarantee or independent security certification is offered.
