---
name: lingxi-system
description: Use when managing Lingxi API Gateway tokens, keys, and account settings. Covers token CRUD, batch operations, usage queries, model list retrieval, search, and account info.
version: 1.2.0
---

Category: provider

# Lingxi System

## Validation

```bash
mkdir -p output/lingxi-system
python -m py_compile skills/lingxi-system/scripts/system_demo.py && echo "py_compile_ok" > output/lingxi-system/validate.txt
```

Pass criteria: command exits 0 and `output/lingxi-system/validate.txt` is generated.

## Output And Evidence

- Save token lists, usage summaries, and operation logs to `output/lingxi-system/`.
- Keep one end-to-end run log for troubleshooting.

## Prerequisites

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install requests
```

- Set `LINGXI_API_KEY` (admin/master token) and `LINGXI_BASE_URL` in environment.

## Token Management

Tokens (令牌) are the primary authentication mechanism for Lingxi API Gateway.

### Token Fields

A token object typically contains:

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Token ID |
| `name` | string | Token name/label |
| `key` | string | The secret API key string |
| `status` | integer | Status code (e.g. 1=active, 2=disabled) |
| `group` | string | Model group binding (comma-separated) |
| `remain_quota` | integer | Remaining quota (50w = 1 USD) |
| `used_quota` | number | Already consumed quota |
| `unlimited_quota` | boolean | Whether quota is unlimited |
| `expired_time` | integer | Expiration timestamp in seconds; `-1` for never |
| `model_limits_enabled` | boolean | Whether model restriction is enabled |
| `model_limits` | string | Allowed model list (comma-separated model names) |
| `allow_ips` | string | Whitelist IPs (newline-separated) |
| `created_at` | string | Creation timestamp |

### List Tokens

**Endpoint**: `GET /api/token/`

**Query Parameters**:
- `p` (string, **required**): page number, e.g. `"0"`
- `size` (string, **required**): page size, e.g. `"10"`

**Headers**:
- `new-api-user` (string, **required**): your account ID, e.g. `"1"`
- `Authorization` (string, **required**): your system token, e.g. `"asasd15a6d165"`

**Response**: wrapped object with token list in `data`.

### Create Token

**Endpoint**: `POST /api/token/`

**Headers**:
- `content-type`: `application/json`
- `new-api-user` (string, **required**): account ID
- `Authorization` (string): system token

**Request Body**:
- `name` (string, **required**): token display name
- `remain_quota` (integer, **required**): quota amount (50w = 1 USD)
- `expired_time` (integer, **required**): expiration timestamp in seconds; `-1` for never
- `unlimited_quota` (boolean, **required**): `true` for unlimited quota
- `model_limits_enabled` (boolean, **required**): enable model restriction
- `model_limits` (string, **required**): comma-separated model names (empty string if none)
- `allow_ips` (string, **required**): whitelist IPs, newline-separated (empty string if none)
- `group` (string, **required**): group name(s), comma-separated

**Response**: wrapped object with created token fields including `key`.

### Get Token Supported Models

**Endpoint**: `GET /v1/models`

**Headers**:
- `content-type`: `application/json`
- `Authorization` (string): system token

Returns the list of models available for the current token or group.

### Get Account Info

**Endpoint**: `GET /api/user/self`

**Headers**:
- `new-api-user` (string, **required**): your account ID
- `Authorization` (string, **required**): your system token

Returns current account details.

### Update Token

**Endpoint**: `PUT /api/token/`

**Headers**:
- `content-type`: `application/json`
- `new-api-user` (string, **required**): account ID
- `Authorization` (string): system token

**Request Body**:
- `id` (integer): token ID to update
- Same fields as create: `name`, `remain_quota`, `expired_time`, `unlimited_quota`, `model_limits_enabled`, `model_limits`, `allow_ips`, `group`

**Response**: wrapped object with updated token.

### Delete Token

**Endpoint**: `DELETE /api/token/{id}/`

**Headers**:
- `content-type`: `application/json`
- `new-api-user` (string, **required**): account ID
- `Authorization` (string): system token

**Response**: success wrapper.

### Search Tokens

**Endpoint**: `GET /api/token/search`

**Query Parameters**:
- `keyword` (string): search by token name
- `token` (string): search by token key, e.g. `sk-xxxxxxxxxxx`

**Headers**:
- `new-api-user` (string, **required**): account ID
- `Authorization` (string, **required**): system token

**Response**: wrapped object with matching token list in `data`.

### Get Token Usage

**Endpoint**: `GET /api/usage/token/`

**Headers**:
- `Authorization` (string, **required**): Bearer token

**Response**:
```json
{
  "code": true,
  "message": "ok",
  "data": {
    "object": "token_usage",
    "name": "我的令牌",
    "total_granted": 1000000,
    "total_used": 250000,
    "total_available": 750000,
    "unlimited_quota": false,
    "model_limits": {},
    "model_limits_enabled": false,
    "expires_at": 1735689600
  }
}
```

Fields:
- `total_granted`: total granted quota
- `total_used`: consumed quota
- `total_available`: remaining quota
- `unlimited_quota`: whether unlimited
- `model_limits`: model restriction map
- `model_limits_enabled`: whether restriction is active
- `expires_at`: expiration timestamp

### Batch Update Tokens

**Endpoint**: `PUT /api/token/batch`

**Headers**:
- `content-type`: `application/json`
- `new-api-user` (string): account ID
- `Authorization` (string): system token

**Request Body**:
- `ids` (array of integer, **required**): token IDs to update, e.g. `[873, 869]`
- `group` (string, optional): group name(s), comma-separated
- `expired_time` (integer, optional): expiration timestamp; `-1` for never
- `remain_quota` (integer, optional): quota (50w = 1 USD)
- `unlimited_quota` (boolean, optional): `true` for unlimited
- `model_limits` (string, optional): comma-separated model names
- `model_limits_enabled` (boolean, optional): enable model restriction
- `allow_ips` (string, optional): whitelist IPs, newline-separated
- `mj_image_mode` (string, optional): image proxy mode, `origin` or `proxy`
- `mj_custom_proxy` (string, optional): custom image proxy address
- `update_fields` (array of string, **required**): list of fields to actually update, e.g. `["group", "expired_time", "remain_quota", "unlimited_quota", "model_limits", "allow_ips", "mj_image_mode", "mj_custom_proxy"]`

**Response**:
```json
{
  "data": 2,
  "success": "true",
  "message": "执行说明"
}
```

- `data`: number of affected rows
- `success`: whether execution succeeded
- `message`: execution description

---

## Quick Start (Python)

```python
import os
import requests

base_url = os.getenv("LINGXI_BASE_URL")
headers = {
    "Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}",
    "new-api-user": "1",
}

# List tokens
resp = requests.get(f"{base_url}/api/token/", headers=headers, params={"p": "0", "size": "10"})
tokens = resp.json().get("data", [])
for t in tokens:
    print(f"{t['id']}: {t['name']} quota={t.get('remain_quota')} used={t.get('used_quota')}")

# Get supported models
resp = requests.get(f"{base_url}/v1/models", headers={"Authorization": headers['Authorization']})
models = resp.json().get("data", [])
print("Available models:", [m.get("id", m.get("name")) for m in models[:5]])

# Get account info
resp = requests.get(f"{base_url}/api/user/self", headers=headers)
user = resp.json().get("data", {})
print("Account:", user)

# Create token
resp = requests.post(f"{base_url}/api/token/", headers=headers, json={
    "name": "my-app-token",
    "group": "default",
    "remain_quota": 250000000000,
    "expired_time": -1,
    "unlimited_quota": False,
    "model_limits_enabled": False,
    "model_limits": "",
    "allow_ips": "",
})
new_token = resp.json().get("data", {})
print("New token key:", new_token.get("key", "")[:12] + "...")

# Get token usage
resp = requests.get(f"{base_url}/api/usage/token/", headers={"Authorization": headers['Authorization']})
usage = resp.json().get("data", {})
print("Usage:", usage)

# Search tokens
resp = requests.get(f"{base_url}/api/token/search", headers=headers, params={"keyword": "app"})
print("Search results:", len(resp.json().get("data", [])))

# Batch update (e.g. disable multiple tokens)
requests.put(f"{base_url}/api/token/batch", headers=headers, json={
    "ids": [new_token.get("id")],
    "unlimited_quota": True,
    "update_fields": ["unlimited_quota"],
})

# Delete token
if new_token.get("id"):
    requests.delete(f"{base_url}/api/token/{new_token['id']}/", headers=headers)
```

---

## Group Management Notes

- Groups control which models and pricing tiers a token can access.
- Different groups may have different model availability and per-token pricing.
- To create a token bound to a specific group, set the `group` field during creation.
- See Lingxi dashboard for group details and pricing.

## Operational Guidance

- Use least-privilege tokens: create dedicated tokens per application/environment.
- Rotate tokens regularly; delete unused tokens to reduce attack surface.
- Monitor token usage to detect anomalies and control costs.
- Do not commit token keys to version control; use env vars or secret managers.
- Use batch update for bulk operations (e.g. disabling all tokens of a departed team member).
- Token quota unit: 500,000 = 1 USD.
- Set `expired_time` to `-1` for tokens that never expire.

## Anti-patterns

- Do not use the master/admin token in application code; create scoped tokens.
- Do not share tokens across untrusted applications.
- Do not ignore token expiration; set reasonable `expired_time` values.
- Do not query usage for every request; cache and batch usage checks.
- Do not omit `update_fields` in batch update; only listed fields are applied.

## Workflow

1) Confirm user intent: list, create, update, delete, search, or query usage.
2) Run one read-only query first to verify admin permissions.
3) Execute the target operation with explicit parameters.
4) Verify results and save output/evidence files.

## References

- See `references/api_reference.md` for full endpoint mapping.
- Source list: `references/sources.md`
- Apifox docs for each endpoint (lines 261-269 and 403-423 in source doc)
