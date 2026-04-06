# Vulnerable Shopping Lab

Intentionally vulnerable Amazon-style e-commerce application for **local security testing only**. Do not deploy to production or expose on the internet.

## Disclaimer

This software contains deliberate security flaws. Use only in isolated lab environments with authorization. The authors are not responsible for misuse.

## Quick start

1. Copy environment file: `cp .env.example .env` (optional overrides).
2. Build and run:

```bash
docker compose up --build -d
```

3. Open the UI: **http://127.0.0.1:18080** (mapped host port `18080` → container `80`; change in `docker-compose.yml` if the port is busy).

4. API base URL (via nginx): `http://127.0.0.1:18080/api/v1/`.

### Default accounts (after seed)

| Email             | Password      | Role  |
|-------------------|---------------|-------|
| admin@lab.local   | admin123      | admin |
| user@lab.local    | UserPass123!  | user  |
| staging@lab.local | staging       | user  |

### Internal lab services (Docker network)

- `http://internal-api:8080/` — fake internal API flag (use SSRF from `api` container).
- `http://metadata:8080/latest/` — fake cloud metadata JSON.

From the host, only the `web` port is published; use the SSRF endpoint (`/api/v1/debug/ssrf`) to reach internal services.

### Dummy files (LFI / disclosure)

- `/app/lab-secrets/passwd` — copy of [database/fake-passwd](database/fake-passwd) (not the host’s `/etc/passwd`).
- `/app/lab-secrets/api-keys.txt` — fake API key file.

### Product images

- **Default:** each product’s `image_url` points at **[Lorem Picsum](https://picsum.photos/)** (`https://picsum.photos/seed/.../400/300`) so the grid shows varied photos without committing large binaries. The **browser** must be able to reach **HTTPS** `picsum.photos` (typical on a networked dev machine).
- **Offline / air-gapped:** put static files under [`frontend/public/images/`](frontend/public/images/) (e.g. SVG or PNG) and set `image_url` to `/images/yourfile.svg` in the DB or via admin; rebuild the `web` image so Vite copies `public/` into the site root.
- **Reseeding:** on API startup, [`backend/seed.py`](backend/seed.py) ensures at least **40** products. If the catalog is smaller (e.g. an old DB with only a few rows), the seed script **truncates** `products` and related tables (`orders`, `cart_items`, `reviews`, etc.) and rebuilds the catalog. Treat this as lab-only data loss.

### Database: `admin_notes` on orders

- New installs get `admin_notes` from [database/init.sql](database/init.sql).
- On startup, the API runs `ALTER TABLE orders ADD COLUMN IF NOT EXISTS admin_notes TEXT` ([`backend/app/__init__.py`](backend/app/__init__.py)) so existing PostgreSQL volumes pick up the column without a manual step.
- Optional manual migration file: [database/migrations/add_admin_notes.sql](database/migrations/add_admin_notes.sql).

## Features

- Register / login / JWT sessions (intentionally weak).
- Product catalog (40+ seeded items with Picsum images), search, sorting, reviews.
- Server-side cart with optional client price override.
- Checkout with coupons, simulated payment, orders and plaintext invoice.
- **Admin dashboard** at `/admin`: metrics, users/orders/payments/products tables, order detail with invoice/refund, tools (ping, config, unauthenticated CSV export). JWT role checks remain flawed by design (VULN-013).

## Architecture

- **web**: nginx + static React (Vite) build; proxies `/api/` to the API.
- **api**: Flask + Gunicorn, PostgreSQL, optional Redis usage in checkout.
- **db**: PostgreSQL with [database/init.sql](database/init.sql).
- **internal-api** / **metadata**: minimal Flask apps for SSRF practice.

## Vulnerability catalog

Each item is intentional. IDs match `VULN-XXX` comments in code where applicable.

| ID | Type | Location | Description | Hint |
|----|------|----------|-------------|------|
| VULN-001 | SQL injection | `GET /api/v1/products/search?q=` | Unsanitized string concatenation into SQL. | Classic `'` / `OR` payloads. |
| VULN-002 | Blind SQLi | `GET /api/v1/products/search-blind?q=` | Boolean-based feedback via count. | Time/blind techniques. |
| VULN-003 | SQL injection (ORDER BY) | `GET /api/v1/products/sorted?sort=&order=` | User input in ORDER BY clause. | Stacked expressions / CASE. |
| VULN-004 | IDOR | `GET /api/v1/products/detail?id=` | Product lookup by id without ownership checks. | Enumerate ids. |
| VULN-005 | Stored XSS | `POST /api/v1/products/<id>/reviews` | Review body stored and rendered unsafely in UI. | `<img onerror=...>` in body. |
| VULN-006 | SSTI | `GET /api/v1/products/preview?name=` | Jinja2 `Template` built from user input. | `{{ config }}` style payloads. |
| VULN-011 | Weak JWT | Auth helpers / `JWT_SECRET` env | Symmetric HS256 with weak default secret. | Brute / guess lab secret. |
| VULN-012 | JWT `none` / unsigned | `decode_token` | Accepts manipulated unsigned tokens. | Forge header `alg: none` or strip verify. |
| VULN-013 | Broken access control (JWT role) | `require_admin` | Admin role taken from token payload. | Set `"role":"admin"` in JWT. |
| VULN-014 | User enumeration | `POST /api/v1/auth/login` | Different errors for unknown user vs bad password. | Compare responses. |
| VULN-015 | Insecure cookie | `POST /api/v1/auth/login` | Token mirrored in cookie without `Secure`. | XSS steals cookie in some setups. |
| VULN-016 | Predictable reset token | `POST /api/v1/auth/forgot-password` | Token derived from weak material; returned in JSON. | Predict token for victim email. |
| VULN-017 | Open redirect | `GET /api/v1/auth/redirect?next=` | Redirects to arbitrary URL. | Phishing / token theft. |
| VULN-018 | Mass assignment | `PATCH /api/v1/users/me` | Client can set `role` and other fields. | Set `"role":"admin"`. |
| VULN-019 | IDOR | `GET /api/v1/users/<user_id>` | Read any user profile when authenticated. | Change `user_id`. |
| VULN-020 | Business logic | `POST /api/v1/cart/items` | Trusts client-supplied `price`. | Negative/zero price. |
| VULN-021 | Business logic | `POST /api/v1/checkout` | Coupons lack per-user limits; stacking. | Send `coupons` array. |
| VULN-022 | Race condition | `POST /api/v1/checkout` | Stock decremented without locking. | Parallel requests (`ab`/`hey`). |
| VULN-023 | Business logic | `POST /api/v1/checkout` | Accepts client `subtotal` / `discount`. | Tamper JSON totals. |
| VULN-024 | Missing authentication | `GET /api/v1/orders/all` | Lists orders without session. | No auth header needed. |
| VULN-025 | IDOR | `GET /api/v1/orders/<order_id>` | Order readable without ownership check. | Iterate order ids. |
| VULN-026 | IDOR | `GET /api/v1/orders/<order_id>/invoice` | Invoice for any order id. | Same as above. |
| VULN-027 | Business logic | `POST /api/v1/orders/<order_id>/duplicate` | Clones order without payment verification. | Replay high-value order. |
| VULN-028 | Payment bypass | `POST /api/v1/payments/<order_id>/capture` | `skip_payment`, zero/negative amounts. | JSON `skip_payment: true`. |
| VULN-029 | Information disclosure | `GET /api/v1/payments/<order_id>/status` | Payment status without auth. | Enumerate orders. |
| VULN-030 | Command injection | `GET /api/v1/admin/ping?host=` | Shell ping with forged admin JWT. | Pipe / subshell in `host`. |
| VULN-031 | Broken access control | `PATCH /api/v1/admin/users/<uid>` | Authenticated user can patch any user (incl. role), not only admin. | Change another user’s `role`. |
| VULN-032 | Business logic | `POST /api/v1/admin/orders/<id>/refund` | Refund amount not capped vs paid. | Request huge refund. |
| VULN-033 | Sensitive data exposure | `GET /api/v1/admin/config` | Returns secrets with admin JWT. | Combine with VULN-013. |
| VULN-034 | Unsafe file upload | `POST /api/v1/admin/upload` | Saves under `/app/uploads` with weak checks. | Upload `.html` / path tricks. |
| VULN-035 | SSRF | `GET/POST /api/v1/debug/ssrf` | Server fetches arbitrary URL. | `http://internal-api:8080/`, `http://metadata:8080/latest/`. |
| VULN-036 | Path traversal / LFI | `GET /api/v1/debug/lfi?file=` | Reads files under lab-secrets. | `file=passwd` → dummy passwd. |
| VULN-037 | Weak path join | `GET /api/v1/debug/lfi-raw?path=` | Naive path handling. | Traversal variants. |
| VULN-038 | Insecure deserialization | `POST /api/v1/debug/import-pickle` | `pickle.loads` on body. | Craft pickle gadget chain. |
| VULN-039 | Unsafe deserialization | `POST /api/v1/debug/import-yaml` | `yaml.unsafe_load`. | YAML gadgets. |
| VULN-040 | Verbose errors | `GET /api/v1/debug/error?msg=` | Raises with stack traces via global handler. | Error-based probing. |
| VULN-041 | Information disclosure | `GET /api/v1/debug/secrets-leak` | Returns fake key file contents. | Direct read. |
| VULN-042 | Information disclosure | `GET /api/v1/health` | Version/build strings. | Fingerprinting. |
| VULN-043 | Web cache deception | `GET /api/v1/cache/user-profile` | Host header reflected with cache headers. | `X-Forwarded-Host` poisoning. |
| VULN-044 | CSRF-friendly | `POST /api/v1/legacy/email` | State change via form post without token. | HTML form from evil site. |
| VULN-045 | GraphQL-style leak | `POST /api/v1/graphql` | Fake introspection with sensitive field names. | Tooling that parses schema. |
| VULN-046 | Reflected XSS (JSON) | `GET /api/v1/search-raw?q=` | Echoes query in JSON. | XSS in poorly coded clients. |
| VULN-047 | Sensitive backup exposure | `GET /api/v1/backup/config.bak` | Old “secret” in JSON. | Credential reuse tests. |
| VULN-048 | Verbose errors | Global exception handler | Returns stack traces in JSON. | Trigger any 500. |
| VULN-049 | Path traversal | `GET /uploads/<fname>` | `send_from_directory` with user path. | `../` sequences. |
| VULN-050 | Directory listing | `GET /uploads-list` | Lists upload directory. | Discover uploaded files. |
| VULN-051 | CORS misconfiguration | Flask-CORS | `CORS_ORIGINS=*` in compose. | Browser-based attacks from any origin. |
| VULN-052 | Default / weak credentials | Seed data | `staging@lab.local` / `staging`; weak admin password. | Credential stuffing. |
| VULN-053 | Security misconfiguration | `.env.example` | Documents weak `JWT_SECRET`. | Key recovery / JWT forge. |
| VULN-054 | Clickjacking / missing CSP | [frontend/nginx.conf](frontend/nginx.conf) | `X-Frame-Options` cleared. | Embed UI in iframe. |
| VULN-055 | Stored XSS | `PATCH /api/v1/admin/orders/<id>` + admin UI | `admin_notes` stored raw; order detail preview uses `dangerouslySetInnerHTML`. | HTML/JS in notes when viewed in admin. |
| VULN-056 | Mass assignment | `PATCH /api/v1/admin/orders/<id>` | JSON keys mapped to `Order` columns (`total`, `user_id`, etc.). | Tamper totals or reassign order owner. |
| VULN-057 | Missing authentication | `GET /api/v1/admin/export/orders` | CSV export of orders + emails without `Authorization`. | `curl` CSV with no token. |
| VULN-058 | CSRF | `POST /api/v1/admin/orders/<id>/refund` | Accepts `application/x-www-form-urlencoded` (no CSRF token). | Evil page POST while admin browser session active. |
| VULN-059 | Log injection | `POST /api/v1/debug/poison-log` | Appends attacker text to `/app/logs/poison.log`. | Prime file for chain. |
| VULN-060 | LFI | `GET /api/v1/debug/read-log?file=` | Reads files under `/app/logs`. | Read poisoned log before SSTI. |
| VULN-061 | SSTI / “RCE” | `GET /api/v1/debug/ssti-from-log?file=` | Entire log file evaluated as Jinja2 template. | After VULN-059, put `{{7*7}}` or config leak payloads in log. |
| VULN-FE-001 | DOM XSS | [frontend/src/pages/Home.tsx](frontend/src/pages/Home.tsx) | `ref` query reflected with `dangerouslySetInnerHTML`. | `?ref=<img src=x onerror=alert(1)>`. |
| VULN-FE-002 | Stored XSS | [frontend/src/pages/Product.tsx](frontend/src/pages/Product.tsx) | Review HTML rendered unsanitized. | Same as API stored XSS. |
| VULN-FE-003 | Prototype pollution (pattern) | [frontend/src/pages/Settings.tsx](frontend/src/pages/Settings.tsx) | Unsafe merge helper (lab demo). | `__proto__` payloads with vulnerable merge. |
| VULN-NGINX-001 | Misconfiguration | [frontend/nginx.conf](frontend/nginx.conf) | Weak security headers on SPA. | Combine with clickjacking. |

### Example exploit chains

1. **Admin takeover**: VULN-018 (`PATCH /users/me` with `"role":"admin"`) or VULN-013 (forge JWT with `"role":"admin"`) → VULN-030 or VULN-033.
2. **SSRF to internal**: VULN-035 with `url=http://internal-api:8080/` or `http://metadata:8080/latest/meta-data/iam/security-credentials/lab-role`.
3. **LFI lab file**: VULN-036 `file=passwd` reads `/app/lab-secrets/passwd` (dummy [database/fake-passwd](database/fake-passwd)).
4. **Payment fraud**: VULN-020 negative line + VULN-023 tampered subtotal + VULN-028 `skip_payment`.
5. **Admin dashboard**: VULN-013 / VULN-018 → open `/admin` → VULN-033 config or VULN-030 ping.
6. **CSV exfil**: VULN-057 `GET /api/v1/admin/export/orders` with no auth → offline correlation of emails and order totals.
7. **Order tampering**: VULN-056 `PATCH` with `payment_status` / `total` / `user_id` after admin access.
8. **Log poison → SSTI (PHP “LFI→RCE” analogue)**: `POST /api/v1/debug/poison-log` with `{"msg":"{{7*7}}"}` → `GET /api/v1/debug/ssti-from-log?file=poison.log` (VULN-059 → VULN-061; optional read-back via VULN-060).

## Development (without Docker)

- Backend: `cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && export DATABASE_URL=... && flask --app wsgi run` (requires PostgreSQL).
- Frontend: `cd frontend && npm install && npm run dev` — proxies `/api` to `localhost:5000`.

## License

Released under the [MIT License](LICENSE). The `LICENSE` file also includes a short scope notice: this project is intentionally insecure and is meant only for authorized security testing in isolated environments.
