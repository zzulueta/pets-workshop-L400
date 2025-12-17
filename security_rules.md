# Security Rules – Focused Security Reviewer
These rules expand the logic used by `agent.md`. They serve as the authoritative security checklist and vulnerability detection guide.

---

# 1. Authentication & Authorization
- Reject patterns where auth checks are missing or performed client-side.
- Flag routes without authentication decorators/middleware.
- Detect role checks based on client-provided values.
- Flag long-lived tokens without expiry.
- Ensure JWTs use HS256/RS256 and are properly verified.
- Reject hard-coded secrets, API keys, or tokens.

**Dangerous Patterns**
- `if user.is_admin:` without verifying identity
- `token = request.args.get("token")` used directly
- Static or hard-coded Authorization tokens

---

# 2. Input Validation & Injection

## SQL Injection
Flag any use of:
- String concatenation in SQL queries  
- f-strings constructing SQL  
- `.format()` in SQL queries  
- Raw queries without parameters  

**Unsafe**
```python
query = f"SELECT * FROM users WHERE id = {user_id}"
```

**Safe**
```python
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

## Command Injection
Flag:
- `os.system()`
- `subprocess.run(..., shell=True)`
- User input flowing into shell commands

## Unsafe Deserialization
Flag:
- `pickle.load`
- `yaml.load` (unsafe loader)
- `eval()` / `exec()`

---

# 3. Sensitive Data Exposure
- Flag printing/logging of passwords, tokens, or PII.
- Identify plaintext storage of credentials.
- Flag unsecured cookies (`Secure`, `HttpOnly`, `SameSite` missing).
- Highlight weak or custom crypto implementations.

**Weak Crypto**
- `hashlib.md5`
- `hashlib.sha1`
- ROT13, base64 as “encryption”
- Custom crypto

---

# 4. File Uploads & File Access
Flag:
- Unvalidated file names
- Saving files using user-controlled paths
- Lack of MIME-type validation
- Insecure temp file creation

**Dangerous**
```python
open(f"uploads/{filename}", "wb")
```

---

# 5. XSS & Frontend Risks

## Reflected / Stored XSS
Flag:
- Direct insertion of user input into HTML.
- Missing escaping or sanitization.

### React
- Any use of `dangerouslySetInnerHTML`
- Direct DOM manipulation:
```js
element.innerHTML = userData;
```

### Flask/Jinja Templates
- Using `| safe` on untrusted values.

---

# 6. SSRF (Server-Side Request Forgery)
Flag:
- `requests.get(user_url)`
- `urllib.request.urlopen(user_url)`
- Fetching arbitrary user-controlled URLs
- Missing allowlists or validation

Warn on:
- Access to cloud metadata endpoints (`169.254.169.254`)

---

# 7. Dependency Vulnerabilities
- Outdated libraries (Python/Node)
- Dependencies with known CVEs
- Absence of lockfiles (`requirements.lock`, `package-lock.json`)
- Use of deprecated packages

---

# 8. Framework-Specific Checks

## Flask
- `debug=True` in production
- Missing CSRF protection (e.g., forms without CSRF tokens)
- Weak `SECRET_KEY`
- Unrestricted file uploads
- Session cookies lacking:
  - `httponly=True`
  - `secure=True`
  - `samesite='Strict' or 'Lax'`

## React
- Storing tokens in `localStorage`
- No CORS restrictions
- Trusting external API responses without sanitization

---

# 9. CI / Configuration Security
Flag:
- Missing `.env` in `.gitignore`
- Secrets in GitHub Actions workflow files
- GitHub Actions triggered by untrusted PRs with `write-all` permissions
- Lack of dependency scanning in CI

---

# 10. Severity Rules
- **Critical**: RCE, SQL injection, XSS, credential exposure, authentication bypass  
- **High**: Broken access control, weak crypto, insecure file uploads  
- **Medium**: Sensitive logging, insecure defaults, outdated dependencies  
- **Low**: Minor hardening, missing documentation for sensitive areas  

---

# 11. Remediation Requirements
Every fix must:
- Be **specific and actionable**
- Use **secure defaults**
- Include **example patched code**
- Include recommended **unit tests** or automated checks to prevent regressions

---
