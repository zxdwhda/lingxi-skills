#!/usr/bin/env python3
"""
Lingxi Image Demo
Compatible with OpenAI SDK and native async platforms
"""
import os
import time
import base64
from openai import OpenAI
import requests


def create_client() -> OpenAI:
    return OpenAI(
        api_key=os.getenv("LINGXI_API_KEY"),
        base_url=os.getenv("LINGXI_BASE_URL"),
    )


def generate_image(prompt: str, model: str = "dall-e-3", size: str = "1024x1024"):
    """OpenAI-compatible sync image generation."""
    client = create_client()
    response = client.images.generate(
        model=model,
        prompt=prompt,
        size=size,
        n=1,
    )
    return response.data[0].url


def edit_image(image_path: str, prompt: str, mask_path: str = None, model: str = "gpt-image-1"):
    """OpenAI-compatible image editing."""
    client = create_client()
    kwargs = {
        "image": open(image_path, "rb"),
        "prompt": prompt,
        "model": model,
    }
    if mask_path:
        kwargs["mask"] = open(mask_path, "rb")
    response = client.images.edit(**kwargs)
    return response.data[0].url


def generate_gpt_image(prompt: str, model: str = "gpt-image-1", size: str = "1024x1024"):
    """GPT Image-1 generation with base64 handling."""
    client = create_client()
    response = client.images.generate(
        model=model,
        prompt=prompt,
        size=size,
        n=1,
    )
    # gpt-image-1 returns base64 by default
    b64 = response.data[0].b64_json
    if b64:
        image_bytes = base64.b64decode(b64)
        output_path = "output/gpt_image.png"
        os.makedirs("output", exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(image_bytes)
        return output_path
    return response.data[0].url


def generate_qwen_image(prompt: str, model: str = "qwen-image-max", size: str = "1328x1328"):
    """Qwen image generation via OpenAI-compatible endpoint."""
    client = create_client()
    response = client.images.generate(
        model=model,
        prompt=prompt,
        size=size,
        n=1,
        extra_body={"watermark": False, "prompt_extend": True},
    )
    return response.data[0].url


def generate_doubao_image(
    prompt: str,
    model: str = "doubao-seedream-5-0-260128",
    size: str = "2K",
    image: str = None,
):
    """Doubao image generation via OpenAI-compatible endpoint."""
    client = create_client()
    kwargs = {
        "model": model,
        "prompt": prompt,
        "size": size,
        "extra_body": {
            "watermark": False,
            "response_format": "url",
        },
    }
    if image:
        kwargs["extra_body"]["image"] = image
    response = client.images.generate(**kwargs)
    return response.data[0].url


def submit_midjourney_imagine(prompt: str, bot_type: str = "MID_JOURNEY") -> str:
    """Submit a Midjourney Imagine task and return task ID."""
    base_url = os.getenv("LINGXI_BASE_URL")
    headers = {"Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}"}
    resp = requests.post(
        f"{base_url}/mj/submit/imagine",
        headers=headers,
        json={"botType": bot_type, "prompt": prompt},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["result"]


def poll_midjourney_task(task_id: str, interval: int = 5, max_attempts: int = 60):
    """Poll Midjourney task until completion or failure."""
    base_url = os.getenv("LINGXI_BASE_URL")
    headers = {"Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}"}
    for _ in range(max_attempts):
        resp = requests.get(
            f"{base_url}/mj/task/{task_id}/fetch",
            headers=headers,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        status = data.get("status", "UNKNOWN")
        progress = data.get("progress", "0%")
        print(f"  Midjourney task {task_id}: {status} ({progress})")
        if status == "SUCCESS":
            return data.get("imageUrl"), data.get("buttons", [])
        if status == "FAILURE":
            raise RuntimeError(f"Midjourney task failed: {data.get('failReason')}")
        time.sleep(interval)
    raise TimeoutError("Midjourney task polling timed out")


def submit_replicate_prediction(model: str, prompt: str, **input_kwargs) -> str:
    """Submit a Replicate prediction and return prediction ID."""
    base_url = os.getenv("LINGXI_BASE_URL")
    headers = {"Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}"}
    payload = {"input": {"prompt": prompt, **input_kwargs}}
    resp = requests.post(
        f"{base_url}/replicate/v1/models/{model}/predictions",
        headers=headers,
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["id"]


def poll_replicate_prediction(prediction_id: str, interval: int = 5, max_attempts: int = 60):
    """Poll Replicate prediction until completion or failure."""
    base_url = os.getenv("LINGXI_BASE_URL")
    headers = {"Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}"}
    for _ in range(max_attempts):
        resp = requests.get(
            f"{base_url}/replicate/v1/predictions/{prediction_id}",
            headers=headers,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        status = data.get("status", "unknown")
        print(f"  Replicate prediction {prediction_id}: {status}")
        if status == "succeeded":
            return data.get("output")
        if status in ("failed", "canceled"):
            raise RuntimeError(f"Replicate prediction {status}: {data.get('error')}")
        time.sleep(interval)
    raise TimeoutError("Replicate prediction polling timed out")


def submit_fal_task(model_path: str, prompt: str, num_images: int = 1, image_urls: list = None) -> str:
    """Submit a Fal.ai task and return request_id."""
    base_url = os.getenv("LINGXI_BASE_URL")
    headers = {"Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}"}
    payload = {"prompt": prompt, "num_images": num_images}
    if image_urls:
        payload["image_urls"] = image_urls
    resp = requests.post(
        f"{base_url}/fal-ai/{model_path}",
        headers=headers,
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["request_id"]


def poll_fal_task(model_path: str, request_id: str, interval: int = 5, max_attempts: int = 60):
    """Poll Fal.ai task until results are available."""
    base_url = os.getenv("LINGXI_BASE_URL")
    headers = {"Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}"}
    for _ in range(max_attempts):
        resp = requests.get(
            f"{base_url}/fal-ai/{model_path}/requests/{request_id}",
            headers=headers,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        if "images" in data:
            return data["images"]
        print(f"  Fal.ai task {request_id}: pending...")
        time.sleep(interval)
    raise TimeoutError("Fal.ai task polling timed out")


def submit_tencent_aigc_task(
    model_name: str,
    model_version: str,
    prompt: str,
    **kwargs,
) -> str:
    """Submit a Tencent AIGC image task and return task ID."""
    base_url = os.getenv("LINGXI_BASE_URL")
    headers = {"Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}"}
    payload = {
        "model_name": model_name,
        "model_version": model_version,
        "prompt": prompt,
        **kwargs,
    }
    resp = requests.post(
        f"{base_url}/tencent-vod/v1/aigc-image",
        headers=headers,
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["Response"]["TaskId"]


def poll_tencent_aigc_task(task_id: str, interval: int = 5, max_attempts: int = 60):
    """Poll Tencent AIGC task until completion."""
    base_url = os.getenv("LINGXI_BASE_URL")
    headers = {"Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}"}
    for _ in range(max_attempts):
        resp = requests.get(
            f"{base_url}/tencent-vod/v1/query/{task_id}",
            headers=headers,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        task = data.get("Response", {}).get("AigcImageTask", {})
        status = task.get("Status", "UNKNOWN")
        progress = task.get("Progress", 0)
        print(f"  Tencent AIGC task {task_id}: {status} ({progress}%)")
        if status == "FINISH":
            files = task.get("Output", {}).get("FileInfos", [])
            return [f.get("FileUrl") for f in files if f.get("FileUrl")]
        time.sleep(interval)
    raise TimeoutError("Tencent AIGC task polling timed out")


if __name__ == "__main__":
    # Example 1: Simple OpenAI-compatible generation
    url = generate_image("A serene Japanese garden with cherry blossoms")
    print("[DALL-E 3] Image URL:", url)

    # Example 2: Qwen image generation
    # url = generate_qwen_image("一只可爱的橘猫坐在窗台上")
    # print("[Qwen] Image URL:", url)

    # Example 3: GPT Image-1 generation (returns base64)
    # path = generate_gpt_image("A hand-drawn cat wearing a wizard hat")
    # print("[GPT Image-1] Saved to:", path)

    # Example 4: Grok image generation
    # url = generate_image("A cat", model="grok-3-image", size="960x960")
    # print("[Grok] Image URL:", url)

    # Example 5: Doubao image generation
    # url = generate_doubao_image(
    #     "充满活力的特写编辑肖像",
    #     model="doubao-seedream-5-0-260128",
    #     size="2K",
    # )
    # print("[Doubao] Image URL:", url)

    # Example 6: Midjourney async flow
    # task_id = submit_midjourney_imagine("A cyberpunk cat warrior")
    # image_url, buttons = poll_midjourney_task(task_id)
    # print("[Midjourney] Image URL:", image_url)
    # print("[Midjourney] Available buttons:", [b["label"] for b in buttons])

    # Example 7: Replicate FLUX async flow
    # pred_id = submit_replicate_prediction(
    #     "black-forest-labs/flux-kontext-dev",
    #     "A beautiful landscape with mountains",
    # )
    # output = poll_replicate_prediction(pred_id)
    # print("[FLUX/Replicate] Output:", output)

    # Example 8: Fal.ai async flow
    # req_id = submit_fal_task("nano-banana", "A cute cat playing piano")
    # images = poll_fal_task("nano-banana", req_id)
    # print("[Fal.ai] Images:", [img["url"] for img in images])

    # Example 9: Fal.ai edit flow
    # req_id = submit_fal_task(
    #     "nano-banana/edit",
    #     "make a photo of the man driving the car",
    #     image_urls=["https://example.com/input.png"],
    # )
    # images = poll_fal_task("nano-banana/edit", req_id)
    # print("[Fal.ai Edit] Images:", [img["url"] for img in images])

    # Example 10: Tencent AIGC async flow
    # task_id = submit_tencent_aigc_task("GEM", "3.0", "A futuristic city")
    # urls = poll_tencent_aigc_task(task_id)
    # print("[Tencent AIGC] URLs:", urls)
