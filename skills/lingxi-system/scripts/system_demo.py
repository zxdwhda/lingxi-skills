#!/usr/bin/env python3
"""
Lingxi System Demo
Demonstrates token CRUD, search, usage queries, batch operations, and account info.
"""
import os
import requests


def get_headers():
    return {
        "Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}",
        "new-api-user": "1",
    }


def get_base_url():
    return os.getenv("LINGXI_BASE_URL", "https://api.aicso.top")


def list_tokens():
    """List all tokens."""
    resp = requests.get(
        f"{get_base_url()}/api/token/",
        headers=get_headers(),
        params={"p": "0", "size": "10"},
    )
    resp.raise_for_status()
    return resp.json().get("data", [])


def get_supported_models():
    """Get models available for the current token/group."""
    resp = requests.get(
        f"{get_base_url()}/v1/models",
        headers={"Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}"},
    )
    resp.raise_for_status()
    return resp.json().get("data", [])


def get_account_info():
    """Get current account info."""
    resp = requests.get(
        f"{get_base_url()}/api/user/self",
        headers=get_headers(),
    )
    resp.raise_for_status()
    return resp.json().get("data", {})


def create_token(name: str, group: str = "default", remain_quota: int = 250000000000):
    """Create a new token."""
    resp = requests.post(
        f"{get_base_url()}/api/token/",
        headers=get_headers(),
        json={
            "name": name,
            "group": group,
            "remain_quota": remain_quota,
            "expired_time": -1,
            "unlimited_quota": False,
            "model_limits_enabled": False,
            "model_limits": "",
            "allow_ips": "",
        },
    )
    resp.raise_for_status()
    return resp.json().get("data", {})


def update_token(token_id: int, **fields):
    """Update a token."""
    payload = {"id": token_id, **fields}
    resp = requests.put(
        f"{get_base_url()}/api/token/",
        headers=get_headers(),
        json=payload,
    )
    resp.raise_for_status()
    return resp.json().get("data", {})


def search_tokens(keyword: str):
    """Search tokens by keyword."""
    resp = requests.get(
        f"{get_base_url()}/api/token/search",
        headers=get_headers(),
        params={"keyword": keyword},
    )
    resp.raise_for_status()
    return resp.json().get("data", [])


def get_token_usage():
    """Get usage statistics for the current token."""
    resp = requests.get(
        f"{get_base_url()}/api/usage/token/",
        headers={"Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}"},
    )
    resp.raise_for_status()
    return resp.json().get("data", {})


def batch_update_tokens(token_ids: list, **fields):
    """Batch update multiple tokens."""
    payload = {"ids": token_ids, **fields}
    resp = requests.put(
        f"{get_base_url()}/api/token/batch",
        headers=get_headers(),
        json=payload,
    )
    resp.raise_for_status()
    return resp.json().get("data", {})


def delete_token(token_id: int):
    """Delete a token."""
    resp = requests.delete(
        f"{get_base_url()}/api/token/{token_id}/",
        headers=get_headers(),
    )
    resp.raise_for_status()
    return resp.json().get("data", {})


if __name__ == "__main__":
    print("=== Lingxi System Demo ===")

    # 1. List tokens
    try:
        tokens = list_tokens()
        print(f"Listed {len(tokens)} tokens")
        for t in tokens[:3]:
            print(f"  ID={t.get('id')} Name={t.get('name')} Status={t.get('status')} Quota={t.get('remain_quota')}")
    except Exception as e:
        print("List tokens failed:", e)

    # 2. Get supported models
    try:
        models = get_supported_models()
        print(f"Supported models: {len(models)}")
        for m in models[:5]:
            print(f"  {m.get('id', m.get('name'))}")
    except Exception as e:
        print("Get models failed:", e)

    # 3. Get account info
    try:
        info = get_account_info()
        print(f"Account: {info}")
    except Exception as e:
        print("Get account info failed:", e)

    # 4. Create a test token
    created = None
    try:
        created = create_token(name="demo-token", group="default", remain_quota=500000)
        print(f"Created token ID={created.get('id')} Key={created.get('key', '')[:12]}...")
    except Exception as e:
        print("Create token failed:", e)

    # 5. Search tokens
    try:
        results = search_tokens("demo")
        print(f"Search 'demo': {len(results)} results")
    except Exception as e:
        print("Search failed:", e)

    # 6. Get usage
    try:
        usage = get_token_usage()
        print(f"Usage: granted={usage.get('total_granted')} used={usage.get('total_used')} available={usage.get('total_available')}")
    except Exception as e:
        print("Get usage failed:", e)

    # 7. Batch update (e.g. set unlimited quota on the demo token)
    if created:
        try:
            batch_update_tokens(
                [created["id"]],
                unlimited_quota=True,
                update_fields=["unlimited_quota"],
            )
            print("Batch updated token unlimited_quota to true")
        except Exception as e:
            print("Batch update failed:", e)

        # 8. Delete the demo token
        try:
            delete_token(created["id"])
            print(f"Deleted demo token ID={created['id']}")
        except Exception as e:
            print("Delete token failed:", e)

    print("=== Demo complete ===")
