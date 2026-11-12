# Issues identified and fixed

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Unsafe archive extraction | High | 61-66 | `tarfile.extractall()` was extracting uploaded files without validation, which could allow path traversal or malicious archive entries. | Switched to a guarded extraction using `filter="data"` and a dedicated `claims_docs` directory. |
| Insecure XML parsing | Medium | 45-54 | The original XML parser accepted untrusted content without protection against XML attacks. | Replaced `xml.etree.ElementTree` with `defusedxml` and kept only valid policy entries. |
| Mutable default argument | Medium | 17-28 | The `discounts=[]` default meant one list was shared across calls, causing odd and repeated state. | Changed the default to `None` and created a new local list inside the function. |
| Insecure network request | Medium | 79-96 | The code used an unverified SSL context and did not validate the URL scheme before fetching data. | Created a secure default SSL context and restricted URLs to `http`/`https` only. |
| Bare except block | Medium | 48-54 | `except:` swallowed all exceptions and hid the real cause of parser failures. | Replaced it with `except ValueError:` so invalid entries are skipped without masking unrelated errors. |
| Hardcoded service values | Medium | 10-14 | The code was binding to all interfaces and stored a fixed token value in source. | Moved the bind host to `127.0.0.1` and generated a secure token using `secrets.token_hex()`. |
