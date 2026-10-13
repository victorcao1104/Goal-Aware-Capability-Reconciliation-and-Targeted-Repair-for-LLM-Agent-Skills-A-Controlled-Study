# Publication and reproduction tooling (2026-10-14)

The author explicitly requested reorganizing code, results and dependencies for future reproduction and publishing them to the named GitHub repository. The destination was inspected: it was empty, public, and writable by the authenticated author account. No existing remote work needed replacement.

This is a bounded extension of the existing artifact workflow. Original scientific inputs remain frozen. Added conveniences:

- One-command offline reanalysis in a separate directory, with evidence/frozen hash checks, summary comparison and byte-identical manuscript-table checks.
- Five regression tests for corrupt evidence, traversal, changed/missing results, nonfinite values and refusing to overwrite existing output. These failed before implementation; the complete suite then passed 61 tests.
- Full 19-package version lock, Python version hint, citation metadata, bilingual entry points and artifact/data-schema guide.
- GitHub Actions with immutable official action revisions, read-only repository permissions, no API secrets, and Linux/Windows jobs.
- Git attributes preserving bytes across platforms so frozen SHA256 identities survive checkout.

The complete dependency lock was installed successfully into a separate fresh directory. The original 30 scientific file hashes still match. The offline helper verifies 3,595 sanitized evidence/accounting records. Public clones omit two original-text-derived frozen datasets and report those omissions explicitly; these are not required for reanalysis and their acquisition instructions remain available.

No new model calls are part of this publication task. The existing API key stays in the ignored local file. Third-party papers and full upstream source bundles are referenced by pinned URLs/commits/hashes rather than republished. No license is invented for the author.

An independent read-only code review found a cross-platform table issue: original tables use CRLF, while default Linux text output would use LF. The post-study table presentation helper now explicitly writes canonical CRLF; no frozen scientific file changed. Local end-to-end testing also exposed Windows realpath retaining `..` in a deep nonexistent destination. The helper now normalizes the absolute path before resolving it. Failed partial reproduction directories are retained for diagnosis and never overwritten.

The initial read-only review of the brainstorming skill was applied as a bounded design check. The user's explicit instruction to improve and upload, together with the established autonomous-work preference, supplies authorization to proceed without another design/permission round. Publication verification outcomes and the remote commit identity are recorded after the checks complete.


The corrected offline helper passed complete reaggregation using the freshly installed pinned dependencies. Both summary JSON files matched recursively within 1e-10 and all three LaTeX tables matched byte-for-byte. The helper left original data untouched. The original 30 file hashes and 3,595 evidence records passed. Linux/Windows CI is configured for the uploaded commit; its remote status must be checked separately.
