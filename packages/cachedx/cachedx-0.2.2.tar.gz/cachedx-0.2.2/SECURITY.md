# Security Policy

## Supported Versions

We actively support the following versions of cachedx with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x   | :white_check_mark: |
| 0.1.x   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability, please follow these steps:

### For Critical Vulnerabilities

**Please do NOT create a public GitHub issue for security vulnerabilities.**

Instead, please:

1. **Email us directly** at security@yourdomain.com (replace with actual email)
2. Include "SECURITY" in the subject line
3. Provide detailed information about the vulnerability
4. Include steps to reproduce the issue
5. Attach any relevant proof-of-concept code (if applicable)

### For Non-Critical Security Issues

For less critical security issues, you may:

1. Create a private security advisory on GitHub
2. Use GitHub's coordinated disclosure process
3. Email us directly (preferred for all security issues)

## What to Include in Your Report

Please provide as much information as possible:

- **Description**: A clear description of the vulnerability
- **Impact**: What could an attacker accomplish with this vulnerability?
- **Reproduction**: Step-by-step instructions to reproduce the issue
- **Environment**: Python version, operating system, cachedx version
- **Code**: Minimal code example that demonstrates the issue
- **Fix suggestions**: If you have ideas for fixing the issue

## Response Timeline

- **Initial Response**: We will acknowledge receipt within 48 hours
- **Investigation**: We will investigate and validate the report within 7 days
- **Fix Timeline**: Critical vulnerabilities will be patched within 30 days
- **Disclosure**: We will coordinate with you on responsible disclosure timing

## Security Best Practices for Users

When using cachedx in production:

### SQL Safety

- Always use the `safe_select()` function for LLM-generated queries
- Never disable SQL safety guards in production
- Validate user input before passing to any cachedx functions

### Data Security

- Use HTTPS for all API endpoints being cached
- Be cautious about caching sensitive data
- Consider data retention policies for cached information
- Review cached data before exposing it via SQL queries

### Network Security

- Configure appropriate firewall rules for DuckDB connections
- Use secure network configurations
- Monitor for unusual data access patterns

### Configuration Security

- Store configuration securely (avoid hardcoded credentials)
- Use environment variables for sensitive settings
- Regularly rotate API keys and access tokens

## Security Updates

Security updates will be:

- Published as patch releases (e.g., 0.2.1 → 0.2.2)
- Documented in the CHANGELOG.md
- Announced via GitHub releases
- Tagged with security labels

## Questions?

If you have questions about this security policy, please email security@yourdomain.com (replace with actual email).
