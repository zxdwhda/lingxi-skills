#!/usr/bin/env python3
"""
Lingxi Audio Demo
Compatible with OpenAI SDK for TTS/ASR.
Also demonstrates Suno music generation, MiniMax TTS, and upload flow.
"""
import os
import time
from openai import OpenAI
import requests


def create_client() -> OpenAI:
    return OpenAI(
        api_key=os.getenv("LINGXI_API_KEY"),
        base_url=os.getenv("LINGXI_BASE_URL"),
    )


def text_to_speech(text: str, model: str = "tts-1", voice: str = "alloy"):
    client = create_client()
    response = client.audio.speech.create(
        model=model,
        voice=voice,
        input=text,
    )
    return response


def speech_to_text(audio_path: str, model: str = "whisper-1"):
    client = create_client()
    with open(audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model=model,
            file=audio_file,
        )
    return transcript


def suno_generate_custom(title: str, tags: str, lyrics: str):
    """Submit a Suno custom mode task and poll for completion."""
    base_url = os.getenv("LINGXI_BASE_URL")
    headers = {"Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}"}

    resp = requests.post(
        f"{base_url}/suno/submit/music",
        headers=headers,
        json={
            "prompt": lyrics,
            "title": title,
            "tags": tags,
            "mv": "chirp-v4",
        },
    )
    resp.raise_for_status()
    task_id = resp.json()["data"]
    print(f"Suno task submitted: {task_id}")

    for _ in range(60):
        status = requests.get(
            f"{base_url}/suno/fetch/{task_id}", headers=headers
        ).json()
        state = status.get("data", {}).get("status", "")
        if state == "SUCCESS":
            return status["data"]
        elif state == "FAILURE":
            raise RuntimeError(f"Suno task failed: {status['data']}")
        time.sleep(10)

    raise TimeoutError("Suno task did not complete in time")


def suno_generate_lyrics(prompt: str):
    """Generate lyrics via Suno."""
    base_url = os.getenv("LINGXI_BASE_URL")
    headers = {"Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}"}

    resp = requests.post(
        f"{base_url}/suno/submit/lyrics",
        headers=headers,
        json={"prompt": prompt},
    )
    resp.raise_for_status()
    return resp.json()["data"]


def minimax_async_tts(text: str, voice_id: str = ""):
    """Submit MiniMax async TTS V2 and poll."""
    base_url = os.getenv("LINGXI_BASE_URL")
    headers = {"Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}"}

    resp = requests.post(
        f"{base_url}/minimax/v1/t2a_async_v2",
        headers=headers,
        json={
            "model": "speech-02-hd",
            "text": text,
            "voice_setting": {
                "voice_id": voice_id or "moss_audio_ce44fc67-7ce3-11f0-8de5-96e35d26fb85",
                "speed": 1,
                "vol": 1,
                "pitch": 0,
            },
            "audio_setting": {
                "format": "mp3",
                "audio_sample_rate": 32000,
                "bitrate": 128000,
                "channel": 2,
            },
        },
    )
    resp.raise_for_status()
    data = resp.json()
    task_id = data["task_id"]
    print(f"MiniMax async TTS submitted: {task_id}")

    for _ in range(30):
        status = requests.get(
            f"{base_url}/minimax/v1/query/t2a_async_query_v2",
            headers=headers,
            params={"task_id": task_id},
        ).json()
        if status.get("status") == "SUCCESS":
            return status
        time.sleep(5)

    raise TimeoutError("MiniMax TTS did not complete in time")


def suno_upload_flow(audio_path: str):
    """Demonstrate Suno upload flow: auth -> S3 -> report -> poll -> init clip."""
    base_url = os.getenv("LINGXI_BASE_URL")
    headers = {"Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}"}

    # 1. Request upload auth
    init_resp = requests.post(
        f"{base_url}/suno/uploads/audio",
        headers=headers,
        json={"extension": "mp3"},
    ).json()
    upload_id = init_resp["data"]["id"]
    presigned_url = init_resp["data"]["url"]
    fields = init_resp["data"]["fields"]
    print(f"Upload ID: {upload_id}")

    # 2. Upload to S3 directly
    with open(audio_path, "rb") as f:
        files = {**{k: (None, v) for k, v in fields.items()}, "file": f}
        s3_resp = requests.post(presigned_url, files=files)
    s3_resp.raise_for_status()
    print("S3 upload done")

    # 3. Report upload done
    requests.post(
        f"{base_url}/suno/uploads/audio/{upload_id}/upload-finish",
        headers=headers,
        json={"upload_type": "file_upload", "upload_filename": os.path.basename(audio_path)},
    )

    # 4. Poll upload status
    for _ in range(30):
        st = requests.get(
            f"{base_url}/suno/uploads/audio/{upload_id}", headers=headers
        ).json()
        if st.get("data", {}).get("status") == "complete":
            print("Upload status complete")
            break
        time.sleep(3)

    # 5. Initialize clip
    clip_resp = requests.post(
        f"{base_url}/suno/uploads/audio/{upload_id}/initialize-clip",
        headers=headers,
        json={},
    ).json()
    clip_id = clip_resp["data"]["clip_id"]
    print(f"Clip ID: {clip_id}")
    return clip_id


if __name__ == "__main__":
    # Demo 1: OpenAI-compatible TTS
    try:
        response = text_to_speech("Hello from Lingxi audio gateway.")
        response.stream_to_file("output_audio.mp3")
        print("Audio saved to output_audio.mp3")
    except Exception as e:
        print("TTS demo skipped:", e)

    # Demo 2: Suno lyrics generation
    try:
        lyrics_data = suno_generate_lyrics("A song about space exploration")
        print("Generated lyrics task ID:", lyrics_data)
    except Exception as e:
        print("Suno lyrics demo skipped:", e)

    # Demo 3: Suno custom mode
    try:
        result = suno_generate_custom(
            title="Demo Track",
            tags="pop",
            lyrics="This is a demo song generated by Lingxi.",
        )
        print("Suno audio URL:", result.get("audio_url"))
    except Exception as e:
        print("Suno generation demo skipped:", e)

    # Demo 4: MiniMax async TTS
    try:
        result = minimax_async_tts("你好，欢迎使用语音合成服务！")
        print("MiniMax TTS file_id:", result.get("file_id"))
    except Exception as e:
        print("MiniMax TTS demo skipped:", e)
