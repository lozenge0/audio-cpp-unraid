# Security

This integration is beta, with no versioned stable release yet. Once released,
maintenance will focus on the current integration template. It does not provide
security maintenance for upstream images, dependencies, models or Unraid itself.

The application port exposes unauthenticated UI/API management. Keep it on trusted
networks and do not expose it directly to the internet. Model storage permissions
and GPU access are described in the [README](README.md#security).

Do not post credentials, private audio or exploitable vulnerability details in
public issues. Use the repository's
**Security → Advisories → Report a vulnerability** option for sensitive integration
reports. If it is unavailable, request a private reporting channel in a public issue
without including sensitive details. Follow upstream's own reporting policy for
vulnerabilities in audio.cpp. Do not assume this integration can fix them.

No response-time guarantee or independent security certification is offered.
