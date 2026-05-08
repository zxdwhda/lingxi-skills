#!/usr/bin/env python3
"""
Lingxi Universal Async Polling Adapter
Supports all platforms with different state codes.
"""
import time
from typing import Callable, Optional


# Platform-specific state configurations
PLATFORM_STATES = {
    # Unified / OpenAI-compatible
    "veo": {
        "success": ["completed"],
        "failure": ["failed"],
        "pending": ["pending", "image_downloading", "video_generating"],
        "state_key": "status",
    },
    "sora": {
        "success": ["completed"],
        "failure": ["failed"],
        "pending": ["pending", "processing"],
        "state_key": "status",
    },
    "grok_video": {
        "success": ["completed"],
        "failure": ["failed"],
        "pending": ["pending", "processing"],
        "state_key": "status",
    },
    # Luma
    "luma": {
        "success": ["completed"],
        "failure": ["failed"],
        "pending": ["queued", "pending", "processing"],
        "state_key": "state",
    },
    # MiniMax (海螺)
    "minimax": {
        "success": ["Success"],
        "failure": ["Failed", "Cancelled"],
        "pending": ["Waiting", "Running"],
        "state_key": "status",
    },
    # Doubao (字节)
    "doubao": {
        "success": ["SUCCEEDED"],
        "failure": ["FAILED"],
        "pending": ["RUNNING", "PENDING", "QUEUED"],
        "state_key": "data.status",  # nested key
    },
    # Kling (可灵)
    "kling": {
        "success": ["succeed"],
        "failure": ["failed"],
        "pending": ["submitted", "processing"],
        "state_key": "task_status",
    },
    # Midjourney
    "midjourney": {
        "success": ["SUCCESS"],
        "failure": ["FAILURE"],
        "pending": ["PENDING", "PROCESSING"],
        "state_key": "status",
    },
    # Replicate
    "replicate": {
        "success": ["succeeded"],
        "failure": ["failed", "canceled"],
        "pending": ["starting", "processing"],
        "state_key": "status",
    },
    # Fal.ai
    "fal.ai": {
        "success": ["COMPLETED"],
        "failure": ["FAILED"],
        "pending": ["IN_QUEUE", "IN_PROGRESS"],
        "state_key": "status",
    },
    # Tencent AIGC
    "tencent": {
        "success": ["FINISH"],
        "failure": ["ABORTED"],
        "pending": ["WAITING", "PROCESSING"],
        "state_key": "Response.Status",
    },
    # Suno
    "suno": {
        "success": ["complete", "completed"],
        "failure": ["failed", "error"],
        "pending": ["pending", "processing"],
        "state_key": "status",
    },
    # Vidu
    "vidu": {
        "success": ["success"],
        "failure": ["failed"],
        "pending": ["created", "queueing", "processing"],
        "state_key": "status",
    },
    # Tongyi Wanxiang
    "tongyi": {
        "success": ["SUCCEEDED"],
        "failure": ["FAILED"],
        "pending": ["PENDING", "RUNNING"],
        "state_key": "output.task_status",
    },
    # Runway
    "runway": {
        "success": ["SUCCEEDED"],
        "failure": ["FAILED"],
        "pending": ["PENDING", "RUNNING", "THROTTLED"],
        "state_key": "status",
    },
}


def _get_nested_value(data: dict, dot_key: str):
    """Get value from nested dict using dot notation like 'data.status'."""
    keys = dot_key.split(".")
    value = data
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None
    return value


def poll_task(
    task_id: str,
    platform: str,
    query_func: Callable[[str], dict],
    interval: int = 10,
    max_attempts: int = 60,
    on_progress: Optional[Callable[[str, dict], None]] = None,
) -> dict:
    """
    Universal async polling for all Lingxi-supported platforms.

    Args:
        task_id: The async task ID.
        platform: One of the keys in PLATFORM_STATES (e.g. "kling", "luma", "midjourney").
        query_func: A function that takes task_id and returns the status dict.
        interval: Seconds between polls. Default 10.
        max_attempts: Max poll attempts. Default 60.
        on_progress: Optional callback(status, full_response) for progress updates.

    Returns:
        The final response dict when task completes.

    Raises:
        ValueError: If platform is not supported.
        RuntimeError: If task fails or max attempts reached.

    Example:
        >>> def query_kling(task_id):
        ...     return requests.get(f"{base}/kling/tasks/{task_id}", headers=headers).json()
        >>> result = poll_task("task-123", "kling", query_kling, interval=15)
    """
    if platform not in PLATFORM_STATES:
        supported = ", ".join(PLATFORM_STATES.keys())
        raise ValueError(f"Unsupported platform '{platform}'. Supported: {supported}")

    config = PLATFORM_STATES[platform]
    state_key = config["state_key"]

    for attempt in range(max_attempts):
        response = query_func(task_id)

        # Extract state value
        if "." in state_key:
            state = _get_nested_value(response, state_key)
        else:
            state = response.get(state_key)

        if state is None:
            raise RuntimeError(f"Could not find state key '{state_key}' in response: {response}")

        # Progress callback
        if on_progress:
            on_progress(state, response)

        # Check completion
        if state in config["success"]:
            return response

        if state in config["failure"]:
            raise RuntimeError(f"Task {task_id} failed with state: {state}. Response: {response}")

        # Still pending, wait and retry
        time.sleep(interval)

    raise RuntimeError(f"Task {task_id} did not complete within {max_attempts} attempts.")


def get_platforms() -> list:
    """Return list of all supported platform names."""
    return list(PLATFORM_STATES.keys())


def get_platform_config(platform: str) -> dict:
    """Return state configuration for a platform."""
    if platform not in PLATFORM_STATES:
        raise ValueError(f"Platform '{platform}' not found.")
    return PLATFORM_STATES[platform]


if __name__ == "__main__":
    # Demo: show all supported platforms
    print("Supported platforms for async polling:")
    for p in get_platforms():
        cfg = get_platform_config(p)
        print(f"  {p}: success={cfg['success']}, failure={cfg['failure']}, key={cfg['state_key']}")
