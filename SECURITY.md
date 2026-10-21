# Security Policy

## Supported Versions

PyLGEN is currently in pre-1.0 development. Security updates are only provided for the latest release in the `0.7.x` series. We strongly recommend always using the latest version available on PyPI.

| Version | Supported          |
| ------- | ------------------ |
| 0.7.3   | :white_check_mark: |
| < 0.7.0 | :x:                |

## Reporting a Vulnerability

We take the security of PyLGEN seriously. Because PyLGEN is a compiler framework that processes potentially untrusted input (source code), we want to ensure any vulnerability (such as crashes/segfaults in the Cython layer) is handled responsibly.

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them using one of the following methods:

1. **GitHub Private Vulnerability Reporting (Preferred):** Go to the **Security** tab of this repository and click on **"Report a vulnerability"**. This allows us to discuss and fix the issue privately.
2. **Email:** If you cannot use GitHub's reporting tool, you can send an email to `yonatanjoseguerraperez@gmail.com`. 

### What to include in your report
To help us assess the issue quickly, please include:
*   A description of the vulnerability and its potential impact.
*   Steps to reproduce the issue (a minimal code snippet is highly appreciated).
*   The version of PyLGEN and Python you are using.
*   Your operating system.

### What to expect from us
*   **Acknowledgment:** We will acknowledge receipt of your vulnerability report within **48-72 hours**.
*   **Updates:** We will keep you informed of our progress at least every **7 days** until the issue is resolved.
*   **Resolution:** If the vulnerability is accepted, we will work on a patch and release it as soon as possible, crediting you in the release notes (unless you prefer to remain anonymous). If the vulnerability is declined (e.g., it is a false positive or a known limitation), we will explain our reasoning.

Thank you for helping keep PyLGEN and its community safe!
