---
name: lingxi-system
description: Use when the user wants to perform admin operations on Lingxi API tokens. Trigger when the user asks to (1) create, update, delete, or search API tokens, (2) check account balance or usage/quota, (3) list available models, or (4) perform any account management task. Note: this skill requires an admin/master token.
---

Category: provider

# Lingxi System

## When to Use

- User wants to create, update, delete, or search API tokens
- User asks about account balance, usage, or quota
- User wants to see which models are available
- User asks "how many tokens left", "create a new key", "manage tokens"

## Configuration

1. Read `LINGXI_API_KEY` from environment. If not set, ask the user.
2. This skill requires an **admin/master token** (not a regular API token)
3. Base URL: `https://api.aicso.top/v1`
4. Most endpoints require `new-api-user` header (account ID, usually `"1"`)

## Intent Routing

| User Says | Action | Endpoint |
|-----------|--------|----------|
| "List tokens", "Show my keys" | List tokens | `GET /api/token/?p=0&size=10` |
| "Create token", "New key" | Create token | `POST /api/token/` |
| "Delete token" | Delete token | `DELETE /api/token/{id}/` |
| "Update token", "Change quota" | Update token | `PUT /api/token/` |
| "Search token" | Search by name/key | `GET /api/token/search` |
| "Check usage", "Balance", "Quota" | Get token usage | `GET /api/usage/token/` |
| "List models" | Get supported models | `GET /v1/models` |
| "Account info" | Get user info | `GET /api/user/self` |
| "Batch update" | Update multiple tokens | `PUT /api/token/batch` |

## Core Code Templates

### Setup

```python
import os
import requests

base_url = os.getenv("LINGXI_BASE_URL", "https://api.aicso.top")
headers = {
    "Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}",
    "new-api-user": "1",
}
```

### List Tokens

```python
resp = requests.get(f"{base_url}/api/token/", headers=headers, params={"p": "0", "size": "10"})
tokens = resp.json().get("data", [])
for t in tokens:
    print(f"{t['id']}: {t['name']} | quota={t.get('remain_quota')} | used={t.get('used_quota')}")
```

### Create Token

```python
resp = requests.post(f"{base_url}/api/token/", headers=headers, json={
    "name": "my-app-token",
    "group": "default",
    "remain_quota": 500000,   # 500k = ~1 USD
    "expired_time": -1,       # -1 = never expire
    "unlimited_quota": False,
    "model_limits_enabled": False,
    "model_limits": "",
    "allow_ips": "",
})
new_token = resp.json().get("data", {})
print("New key:", new_token.get("key", "")[:16] + "...")
```

### Get Token Usage / Balance

```python
resp = requests.get(f"{base_url}/api/usage/token/", headers={"Authorization": headers["Authorization"]})
usage = resp.json().get("data", {})
print(f"Granted: {usage.get('total_granted')}")
print(f"Used: {usage.get('total_used')}")
print(f"Available: {usage.get('total_available')}")
```

### Search Tokens

```python
resp = requests.get(f"{base_url}/api/token/search", headers=headers, params={"keyword": "app"})
results = resp.json().get("data", [])
print(f"Found {len(results)} tokens")
```

### Batch Update

```python
resp = requests.put(f"{base_url}/api/token/batch", headers=headers, json={
    "ids": [123, 456],
    "group": "default",
    "update_fields": ["group"],
})
print("Updated:", resp.json().get("data"), "tokens")
```

### Delete Token

```python
token_id = 123
requests.delete(f"{base_url}/api/token/{token_id}/", headers=headers)
print(f"Token {token_id} deleted")
```

## Token Quota Notes

- Quota unit: **500,000 = 1 USD**
- `remain_quota`: remaining balance in quota units
- `used_quota`: consumed amount
- Set `unlimited_quota: True` for unlimited tokens
- Set `expired_time: -1` for tokens that never expire
- Use `model_limits` to restrict which models a token can access

## Common Errors

| Code | Meaning | Fix |
|------|---------|-----|
| 401 | Admin token invalid | Check `LINGXI_API_KEY` is a master token |
| 403 | Not admin | Use the account owner token |

## Error Handling

- **"无权进行此操作，access token 无效"** → The API key is not an admin/master token. System operations require the account owner's master key.
- **"Invalid URL"** → System endpoints use `https://api.aicso.top` without `/v1` prefix.
- **"无可用渠道"** → Some models may be restricted in the current group. Check the model list.

## Anti-patterns

- Do NOT use admin tokens in application code; create scoped tokens instead
- Do NOT commit token keys to version control
- Do NOT query usage for every request; cache results
- Do NOT omit `update_fields` in batch update

## Workflow

1. Confirm user intent (list/create/update/delete/search/usage)
2. Verify admin permissions with a read-only query first
3. Execute the operation
4. Report results clearly (show key prefix, quota, group)
