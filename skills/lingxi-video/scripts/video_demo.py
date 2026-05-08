#!/usr/bin/env python3
"""
Lingxi Video Demo
Demonstrates OpenAI-compatible and native async video generation via Lingxi API Gateway.
Supports: Sora (OpenAI/Unified/Chat), Veo (Unified/OpenAI), Grok (Unified/OpenAI),
Luma (native), MiniMax/海螺 (native), Kling (native), Doubao (native), Fal.ai (native).
"""
import os
import time
from typing import Optional

import requests
from openai import OpenAI


def create_client() -> OpenAI:
    """Create an OpenAI client pointing to Lingxi gateway."""
    return OpenAI(
        api_key=os.getenv("LINGXI_API_KEY"),
        base_url=os.getenv("LINGXI_BASE_URL"),
    )


def generate_video_openai(prompt: str, model: str = "sora-2", image_path: Optional[str] = None):
    """
    OpenAI-compatible video generation (Sora, Veo OpenAI format, Grok OpenAI format).
    Returns the response object (may contain video_url or task_id depending on platform).
    """
    client = create_client()
    kwargs = {"model": model, "prompt": prompt}
    if image_path:
        kwargs["image"] = open(image_path, "rb")
    response = client.video.generations.create(**kwargs)
    return response


def poll_task(base_url: str, api_key: str, endpoint: str, task_id: str,
              state_key: str = "state", completed_value: str = "completed",
              failed_values: tuple = ("failed", "error", "FAILURE"),
              max_retries: int = 60, interval: int = 10):
    """
    Generic async task polling helper.

    Args:
        base_url: Lingxi base URL
        api_key: Lingxi API key
        endpoint: polling endpoint template, e.g. '/luma/generations/{task_id}'
        task_id: the task / request ID to poll
        state_key: JSON key path for status (dot-notation supported, e.g. 'data.state')
        completed_value: value indicating completion
        failed_values: values indicating failure
        max_retries: max poll attempts
        interval: seconds between polls

    Returns:
        Final JSON response dict, or raises TimeoutError.
    """
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{base_url}{endpoint.format(task_id=task_id)}"

    for attempt in range(max_retries):
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        # Navigate nested state key
        value = data
        for key in state_key.split("."):
            value = value.get(key, {}) if isinstance(value, dict) else {}
        status = value if isinstance(value, str) else "unknown"

        print(f"  Poll {attempt + 1}/{max_retries}: status = {status}")

        if status == completed_value:
            return data
        if status in failed_values:
            raise RuntimeError(f"Task failed: {data}")

        time.sleep(interval)

    raise TimeoutError(f"Task {task_id} did not complete within {max_retries * interval}s")


# ---------------------------------------------------------------------------
# Veo Unified Format
# ---------------------------------------------------------------------------

def veo_unified_create_and_poll(prompt: str, model: str = "veo3.1-fast",
                                 images: Optional[list] = None,
                                 aspect_ratio: Optional[str] = None):
    """
    Veo unified format: POST /v1/video/create -> GET /v1/video/query?id={id}
    """
    base_url = os.getenv("LINGXI_BASE_URL", "").rstrip("/")
    api_key = os.getenv("LINGXI_API_KEY", "")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    payload = {"model": model, "prompt": prompt}
    if images:
        payload["images"] = images
    if aspect_ratio:
        payload["aspect_ratio"] = aspect_ratio

    submit_resp = requests.post(f"{base_url}/v1/video/create", headers=headers, json=payload, timeout=30)
    submit_resp.raise_for_status()
    task_id = submit_resp.json()["id"]
    print(f"Veo unified task submitted: {task_id}")

    result = poll_task(
        base_url, api_key,
        endpoint="/v1/video/query?id={task_id}",
        task_id=task_id,
        state_key="status",
        completed_value="completed",
        failed_values=("failed", "error", "video_generation_failed", "video_upsampling_failed"),
    )
    video_url = result.get("video_url") or result.get("upsample_video_url")
    print(f"Veo video ready: {video_url}")
    return result


# ---------------------------------------------------------------------------
# Veo OpenAI Format
# ---------------------------------------------------------------------------

def veo_openai_create_and_poll(prompt: str, model: str = "veo_3_1",
                                image_path: Optional[str] = None,
                                seconds: str = "8", size: str = "16x9"):
    """
    Veo OpenAI format: POST /v1/videos -> GET /v1/videos/{id}
    """
    base_url = os.getenv("LINGXI_BASE_URL", "").rstrip("/")
    api_key = os.getenv("LINGXI_API_KEY", "")
    headers = {"Authorization": f"Bearer {api_key}"}

    files = {}
    data = {"model": model, "prompt": prompt, "seconds": seconds, "size": size}
    if image_path:
        files["input_reference"] = open(image_path, "rb")

    submit_resp = requests.post(f"{base_url}/v1/videos", headers=headers, data=data, files=files, timeout=30)
    submit_resp.raise_for_status()
    task_id = submit_resp.json()["id"]
    print(f"Veo OpenAI task submitted: {task_id}")

    result = poll_task(
        base_url, api_key,
        endpoint="/v1/videos/{task_id}",
        task_id=task_id,
        state_key="status",
        completed_value="completed",
        failed_values=("failed", "error"),
    )
    video_url = result.get("video_url")
    print(f"Veo OpenAI video ready: {video_url}")
    return result


# ---------------------------------------------------------------------------
# Luma Native
# ---------------------------------------------------------------------------

def luma_submit_and_poll(prompt: str, image_url: Optional[str] = None,
                         image_end_url: Optional[str] = None,
                         model_name: str = "ray-v2"):
    """
    Luma native format: POST /luma/generations -> GET /luma/generations/{task_id}
    States: queued -> pending -> processing -> completed / failed
    """
    base_url = os.getenv("LINGXI_BASE_URL", "").rstrip("/")
    api_key = os.getenv("LINGXI_API_KEY", "")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    payload = {
        "user_prompt": prompt,
        "model_name": model_name,
        "duration": "5s",
        "resolution": "720p",
    }
    if image_url:
        payload["image_url"] = image_url
    if image_end_url:
        payload["image_end_url"] = image_end_url

    submit_resp = requests.post(f"{base_url}/luma/generations", headers=headers, json=payload, timeout=30)
    submit_resp.raise_for_status()
    task_id = submit_resp.json()["data"]["task_id"]
    print(f"Luma task submitted: {task_id}")

    result = poll_task(
        base_url, api_key,
        endpoint="/luma/generations/{task_id}",
        task_id=task_id,
        state_key="state",
        completed_value="completed",
        failed_values=("failed", "error"),
    )
    video_url = result.get("video", {}).get("url") or result.get("video_url")
    print(f"Luma video ready: {video_url}")
    return result


# ---------------------------------------------------------------------------
# Runway Native
# ---------------------------------------------------------------------------

def runway_submit_and_poll(prompt_image: str, prompt_text: str,
                           model: str = "gen4_turbo", ratio: str = "1280:768",
                           duration: int = 5):
    """
    Runway native: POST /runwayml/v1/image_to_video -> GET /runwayml/v1/tasks/{task_id}
    """
    base_url = os.getenv("LINGXI_BASE_URL", "").rstrip("/")
    api_key = os.getenv("LINGXI_API_KEY", "")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    payload = {
        "promptImage": prompt_image,
        "promptText": prompt_text,
        "model": model,
        "ratio": ratio,
        "duration": duration,
    }
    submit_resp = requests.post(f"{base_url}/runwayml/v1/image_to_video", headers=headers, json=payload, timeout=30)
    submit_resp.raise_for_status()
    task_id = submit_resp.json()["data"]["task_id"]
    print(f"Runway task submitted: {task_id}")

    result = poll_task(
        base_url, api_key,
        endpoint="/runwayml/v1/tasks/{task_id}",
        task_id=task_id,
        state_key="data.task_status",
        completed_value="completed",
        failed_values=("failed", "error", "FAILURE"),
    )
    print(f"Runway result: {result}")
    return result


# ---------------------------------------------------------------------------
# MiniMax (海螺) Native
# ---------------------------------------------------------------------------

def minimax_submit_and_poll(prompt: str, model: str = "MiniMax-Hailuo-02",
                            duration: int = 10,
                            first_frame_image: Optional[str] = None,
                            last_frame_image: Optional[str] = None):
    """
    MiniMax native: POST /minimax/v1/video_generation -> GET /minimax/v1/query/video_generation?task_id={task_id}
    Status: Waiting -> Running -> Success / Failed / Cancelled
    """
    base_url = os.getenv("LINGXI_BASE_URL", "").rstrip("/")
    api_key = os.getenv("LINGXI_API_KEY", "")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    payload = {"model": model, "prompt": prompt, "duration": duration}
    if first_frame_image:
        payload["first_frame_image"] = first_frame_image
    if last_frame_image:
        payload["last_frame_image"] = last_frame_image

    submit_resp = requests.post(f"{base_url}/minimax/v1/video_generation", headers=headers, json=payload, timeout=30)
    submit_resp.raise_for_status()
    task_id = submit_resp.json()["task_id"]
    print(f"MiniMax task submitted: {task_id}")

    result = poll_task(
        base_url, api_key,
        endpoint="/minimax/v1/query/video_generation?task_id={task_id}",
        task_id=task_id,
        state_key="data.status",
        completed_value="Success",
        failed_values=("Failed", "Cancelled"),
    )
    video_url = result.get("data", {}).get("file", {}).get("download_url")
    print(f"MiniMax video ready: {video_url}")
    return result


# ---------------------------------------------------------------------------
# Doubao Native
# ---------------------------------------------------------------------------

def doubao_create_and_poll(prompt: str, model: str = "doubao-seedance-1-5-pro-251215",
                           first_frame_url: Optional[str] = None,
                           last_frame_url: Optional[str] = None,
                           generate_audio: bool = True):
    """
    Doubao native: POST /volc/v1/contents/generations/tasks -> GET /volc/v1/contents/generations/tasks/{task_id}
    """
    base_url = os.getenv("LINGXI_BASE_URL", "").rstrip("/")
    api_key = os.getenv("LINGXI_API_KEY", "")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    content = [{"type": "text", "text": prompt}]
    if first_frame_url:
        item = {"type": "image_url", "image_url": {"url": first_frame_url}, "role": "first_frame"}
        content.append(item)
    if last_frame_url:
        item = {"type": "image_url", "image_url": {"url": last_frame_url}, "role": "last_frame"}
        content.append(item)

    payload = {"model": model, "content": content, "generate_audio": generate_audio}

    submit_resp = requests.post(f"{base_url}/volc/v1/contents/generations/tasks", headers=headers, json=payload, timeout=30)
    submit_resp.raise_for_status()
    task_id = submit_resp.json()["id"]
    print(f"Doubao task submitted: {task_id}")

    result = poll_task(
        base_url, api_key,
        endpoint="/volc/v1/contents/generations/tasks/{task_id}",
        task_id=task_id,
        state_key="status",
        completed_value="succeeded",
        failed_values=("failed",),
    )
    video_url = result.get("content", {}).get("video_url")
    print(f"Doubao video ready: {video_url}")
    return result


# ---------------------------------------------------------------------------
# Kling Native
# ---------------------------------------------------------------------------

def kling_submit_and_poll(prompt: str, mode: str = "text-to-video",
                          image_url: Optional[str] = None, duration: int = 5):
    """
    Kling native: POST /kling/{mode} -> GET /kling/tasks/{task_id}
    """
    base_url = os.getenv("LINGXI_BASE_URL", "").rstrip("/")
    api_key = os.getenv("LINGXI_API_KEY", "")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    payload = {"prompt": prompt, "duration": duration}
    if image_url:
        payload["image_url"] = image_url

    submit_resp = requests.post(f"{base_url}/kling/{mode}", headers=headers, json=payload, timeout=30)
    submit_resp.raise_for_status()
    task_id = submit_resp.json()["data"]["task_id"]
    print(f"Kling task submitted: {task_id}")

    result = poll_task(
        base_url, api_key,
        endpoint="/kling/tasks/{task_id}",
        task_id=task_id,
        state_key="data.state",
        completed_value="completed",
        failed_values=("failed",),
    )
    video_url = result.get("data", {}).get("video_url")
    print(f"Kling video ready: {video_url}")
    return result


# ---------------------------------------------------------------------------
# Fal.ai Veo3
# ---------------------------------------------------------------------------

def fal_veo3_submit_and_poll(prompt: str, image_url: Optional[str] = None, fast: bool = False):
    """
    Fal.ai native Veo 3: POST /fal-ai/veo3[/fast][/image-to-video] -> GET /fal-ai/veo3/requests/{request_id}
    """
    base_url = os.getenv("LINGXI_BASE_URL", "").rstrip("/")
    api_key = os.getenv("LINGXI_API_KEY", "")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    if image_url:
        path = f"/fal-ai/veo3{'/fast' if fast else ''}/image-to-video"
        payload = {"prompt": prompt, "image_url": image_url}
    else:
        path = f"/fal-ai/veo3{'/fast' if fast else ''}"
        payload = {"prompt": prompt}

    submit_resp = requests.post(f"{base_url}{path}", headers=headers, json=payload, timeout=30)
    submit_resp.raise_for_status()
    request_id = submit_resp.json().get("request_id")
    print(f"Fal.ai Veo3 task submitted: {request_id}")

    result = poll_task(
        base_url, api_key,
        endpoint="/fal-ai/veo3/requests/{task_id}",
        task_id=request_id,
        state_key="status",
        completed_value="COMPLETED",
        failed_values=("FAILED",),
    )
    video_url = result.get("video", {}).get("url") or result.get("output", {}).get("video_url")
    print(f"Fal.ai Veo3 video ready: {video_url}")
    return result


# ---------------------------------------------------------------------------
# Tongyi Wanxiang
# ---------------------------------------------------------------------------

def tongyi_wanxiang_create_and_poll(prompt: str, img_url: str, model: str = "wan2.5-i2v-preview",
                                      resolution: str = "480P", duration: int = 5):
    """
    Tongyi Wanxiang: POST /alibailian/api/v1/services/aigc/video-generation/video-synthesis
    -> GET /alibailian/api/v1/tasks/{task_id}
    """
    base_url = os.getenv("LINGXI_BASE_URL", "").rstrip("/")
    api_key = os.getenv("LINGXI_API_KEY", "")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    payload = {
        "model": model,
        "input": {"prompt": prompt, "img_url": img_url},
        "parameters": {"resolution": resolution, "duration": duration, "prompt_extend": True, "watermark": False},
    }
    submit_resp = requests.post(f"{base_url}/alibailian/api/v1/services/aigc/video-generation/video-synthesis", headers=headers, json=payload, timeout=30)
    submit_resp.raise_for_status()
    task_id = submit_resp.json()["output"]["task_id"]
    print(f"Tongyi Wanxiang task submitted: {task_id}")

    result = poll_task(
        base_url, api_key,
        endpoint="/alibailian/api/v1/tasks/{task_id}",
        task_id=task_id,
        state_key="output.task_status",
        completed_value="SUCCEEDED",
        failed_values=("FAILED",),
    )
    video_url = result.get("output", {}).get("video_url")
    print(f"Tongyi Wanxiang video ready: {video_url}")
    return result


# ---------------------------------------------------------------------------
# Grok Unified Format
# ---------------------------------------------------------------------------

def grok_unified_create_and_poll(prompt: str, model: str = "grok-video-3",
                                  aspect_ratio: str = "3:2", size: str = "720P",
                                  images: Optional[list] = None):
    """
    Grok unified: POST /v1/video/create -> GET /v1/video/query?id={id}
    """
    base_url = os.getenv("LINGXI_BASE_URL", "").rstrip("/")
    api_key = os.getenv("LINGXI_API_KEY", "")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    payload = {"model": model, "prompt": prompt, "aspect_ratio": aspect_ratio, "size": size}
    if images:
        payload["images"] = images

    submit_resp = requests.post(f"{base_url}/v1/video/create", headers=headers, json=payload, timeout=30)
    submit_resp.raise_for_status()
    task_id = submit_resp.json()["id"]
    print(f"Grok unified task submitted: {task_id}")

    result = poll_task(
        base_url, api_key,
        endpoint="/v1/video/query?id={task_id}",
        task_id=task_id,
        state_key="status",
        completed_value="completed",
        failed_values=("failed", "error"),
    )
    video_url = result.get("video_url")
    print(f"Grok video ready: {video_url}")
    return result


if __name__ == "__main__":
    # Example 1: OpenAI-compatible text-to-video (Sora)
    print("=== Example 1: OpenAI-compatible text-to-video ===")
    result = generate_video_openai("A panda eating bamboo in a misty forest", model="sora-2")
    print("Video result:", result)

    # Example 2: Veo unified format
    # print("\n=== Example 2: Veo unified ===")
    # veo_unified_create_and_poll("A serene tropical beach sunset", model="veo3.1-fast", aspect_ratio="16:9")

    # Example 3: Luma native async
    # print("\n=== Example 3: Luma native ===")
    # luma_submit_and_poll("A neon-lit cyberpunk street at night")

    # Example 4: MiniMax native async
    # print("\n=== Example 4: MiniMax native ===")
    # minimax_submit_and_poll("A koi fish swimming in a pond", duration=10)

    # Example 5: Doubao native async
    # print("\n=== Example 5: Doubao native ===")
    # doubao_create_and_poll("A serene mountain lake at sunrise", model="doubao-seedance-1-5-pro-251215")

    # Example 6: Kling native async
    # print("\n=== Example 6: Kling native ===")
    # kling_submit_and_poll("A dragon flying over a mountain", mode="text-to-video", duration=5)

    # Example 7: Fal.ai Veo3
    # print("\n=== Example 7: Fal.ai Veo3 ===")
    # fal_veo3_submit_and_poll("Aerial view of ocean waves crashing on rocks")

    # Example 8: Tongyi Wanxiang
    # print("\n=== Example 8: Tongyi Wanxiang ===")
    # tongyi_wanxiang_create_and_poll("Change lighting to golden hour", img_url="https://example.com/image.png")

    # Example 9: Grok unified
    # print("\n=== Example 9: Grok unified ===")
    # grok_unified_create_and_poll("A cat eating fish", model="grok-video-3")
