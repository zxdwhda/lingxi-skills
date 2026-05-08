#!/usr/bin/env python3
"""
Lingxi Chat Demo
Compatible with OpenAI SDK + raw requests for provider-native formats.
Base URL: https://api.aicso.top/v1
"""
import base64
import json
import os
from pathlib import Path

from openai import OpenAI


def create_client() -> OpenAI:
    return OpenAI(
        api_key=os.getenv("LINGXI_API_KEY"),
        base_url=os.getenv("LINGXI_BASE_URL"),
    )


# ---------------------------------------------------------------------------
# OpenAI-compatible Chat Completions
# ---------------------------------------------------------------------------

def chat_completion(prompt: str, model: str = "gpt-4o-mini", stream: bool = False):
    """Basic chat completion (OpenAI-compatible format)."""
    client = create_client()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=stream,
    )
    if stream:
        content = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                content += chunk.choices[0].delta.content
                print(chunk.choices[0].delta.content, end="", flush=True)
        print()
        return content
    else:
        print(response.choices[0].message.content)
        return response.choices[0].message.content


def chat_with_image_url(image_url: str, prompt: str = "Describe this image", model: str = "gpt-4o"):
    """Vision with remote image URL (OpenAI-compatible)."""
    client = create_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ],
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content


def chat_with_image_file(image_path: str, prompt: str = "Describe this image", model: str = "gpt-4o"):
    """Vision with local base64 image (OpenAI-compatible)."""
    client = create_client()
    path = Path(image_path)
    b64 = base64.b64encode(path.read_bytes()).decode("utf-8")
    mime = f"image/{path.suffix.lstrip('.')}" if path.suffix else "image/png"
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                ],
            }
        ],
        max_tokens=300,
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content


def chat_with_function_calling(prompt: str = "What's the weather in Beijing?", model: str = "gpt-4o"):
    """Function calling demo (OpenAI-compatible)."""
    client = create_client()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get current weather for a city",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {"type": "string", "description": "City name"},
                            "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                        },
                        "required": ["city"],
                    },
                },
            }
        ],
    )
    msg = response.choices[0].message
    print("Content:", msg.content)
    if msg.tool_calls:
        print("Tool calls:", msg.tool_calls)
    return msg


def chat_structured_output(prompt: str = "Return a JSON with name and age keys", model: str = "gpt-4.1-2025-04-14"):
    """Structured output demo with json_schema (OpenAI-compatible)."""
    client = create_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful data extractor."},
            {"role": "user", "content": prompt},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "person_info",
                "description": "Extract person information",
                "schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "integer"},
                    },
                    "required": ["name", "age"],
                    "additionalProperties": False,
                },
                "strict": True,
            }
        },
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content


def chat_with_reasoning(prompt: str = "Solve 2+2 step by step", model: str = "o4-mini"):
    """Reasoning model with effort control (OpenAI-compatible)."""
    client = create_client()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        reasoning_effort="medium",
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content


def chat_with_thinking_deepseek(prompt: str = "Hello", model: str = "deepseek-v3-1-250821"):
    """DeepSeek v3.1 with thinking control."""
    client = create_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1000,
        stream=True,
        stream_options={"include_usage": True},
        thinking={"type": "enabled"},
    )
    content = ""
    for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            content += chunk.choices[0].delta.content
            print(chunk.choices[0].delta.content, end="", flush=True)
    print()
    return content


def chat_with_web_search(prompt: str = "What was a positive news story from today?"):
    """Web search via gpt-4o-search-preview."""
    client = create_client()
    response = client.chat.completions.create(
        model="gpt-4o-search-preview",
        web_search_options={},
        messages=[{"role": "user", "content": prompt}],
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content


# ---------------------------------------------------------------------------
# Embeddings
# ---------------------------------------------------------------------------

def create_embedding(text: str, model: str = "text-embedding-3-small"):
    """Text embeddings (OpenAI-compatible)."""
    client = create_client()
    response = client.embeddings.create(
        model=model,
        input=text,
    )
    emb = response.data[0].embedding
    print(f"Embedding dim: {len(emb)}, first 5: {emb[:5]}")
    return emb


# ---------------------------------------------------------------------------
# Audio APIs
# ---------------------------------------------------------------------------

def transcribe_audio(audio_path: str, model: str = "whisper-1"):
    """Speech-to-text transcription."""
    client = create_client()
    with open(audio_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model=model,
            file=f,
        )
    print("Transcript:", transcript.text)
    return transcript.text


def transcribe_audio_with_timestamps(audio_path: str, model: str = "whisper-1"):
    """Speech-to-text with word-level timestamps."""
    client = create_client()
    with open(audio_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model=model,
            file=f,
            response_format="verbose_json",
            timestamp_granularities=["word"],
        )
    print("Words:", transcript.words)
    return transcript.words


def text_to_speech(text: str, voice: str = "alloy", output_path: str = "output.mp3"):
    """Text-to-speech synthesis."""
    client = create_client()
    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        input=text,
        voice=voice,
    )
    response.stream_to_file(output_path)
    print(f"Saved speech to {output_path}")
    return output_path


def chat_with_audio_output(prompt: str = "Say hello in a friendly tone", model: str = "gpt-4o-audio-preview"):
    """GPT-4o-audio with audio output."""
    client = create_client()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        modalities=["text", "audio"],
        audio={"voice": "alloy", "format": "wav"},
    )
    msg = response.choices[0].message
    print("Text:", msg.content)
    if msg.audio:
        print("Audio data length:", len(msg.audio.data) if hasattr(msg.audio, "data") else "N/A")
    return msg


# ---------------------------------------------------------------------------
# Claude Native Format (raw requests)
# ---------------------------------------------------------------------------

def claude_native_message(prompt: str, model: str = "claude-sonnet-4-20250514"):
    """Claude native format via raw requests."""
    import requests

    headers = {
        "x-api-key": os.getenv("LINGXI_API_KEY"),
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": model,
        "max_tokens": 4096,
        "system": "You are a helpful assistant.",
        "messages": [{"role": "user", "content": prompt}],
    }
    resp = requests.post(
        f"{os.getenv('LINGXI_BASE_URL')}/v1/messages",
        headers=headers,
        json=payload,
    )
    resp.raise_for_status()
    data = resp.json()
    text_blocks = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
    print("Claude native:", "".join(text_blocks))
    return data


def claude_native_with_pdf(pdf_url: str, prompt: str = "Summarize this PDF", model: str = "claude-haiku-4-5-20251001"):
    """Claude native format with PDF document."""
    import requests

    headers = {
        "x-api-key": os.getenv("LINGXI_API_KEY"),
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": model,
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "document",
                        "source": {"type": "url", "url": pdf_url},
                    },
                ],
            }
        ],
    }
    resp = requests.post(
        f"{os.getenv('LINGXI_BASE_URL')}/v1/messages",
        headers=headers,
        json=payload,
    )
    resp.raise_for_status()
    data = resp.json()
    text_blocks = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
    print("Claude PDF summary:", "".join(text_blocks))
    return data


def claude_native_with_thinking(prompt: str = "Explain quantum computing", model: str = "claude-sonnet-4-20250514"):
    """Claude native format with thinking enabled."""
    import requests

    headers = {
        "x-api-key": os.getenv("LINGXI_API_KEY"),
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": model,
        "max_tokens": 8000,
        "thinking": {"type": "enabled", "budget_tokens": 1200},
        "messages": [{"role": "user", "content": prompt}],
    }
    resp = requests.post(
        f"{os.getenv('LINGXI_BASE_URL')}/v1/messages",
        headers=headers,
        json=payload,
    )
    resp.raise_for_status()
    data = resp.json()
    thinking_blocks = [b["thinking"] for b in data.get("content", []) if b.get("type") == "thinking"]
    text_blocks = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
    print("Thinking:", "".join(thinking_blocks))
    print("Answer:", "".join(text_blocks))
    return data


def claude_native_with_tools(prompt: str = "What is the weather in San Francisco?", model: str = "claude-sonnet-4-20250514"):
    """Claude native format with function calling."""
    import requests

    headers = {
        "x-api-key": os.getenv("LINGXI_API_KEY"),
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": model,
        "max_tokens": 1024,
        "tools": [
            {
                "name": "get_weather",
                "description": "Get the current weather in a given location",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "The city and state, e.g. San Francisco, CA"}
                    },
                    "required": ["location"]
                }
            }
        ],
        "messages": [{"role": "user", "content": prompt}],
    }
    resp = requests.post(
        f"{os.getenv('LINGXI_BASE_URL')}/v1/messages",
        headers=headers,
        json=payload,
    )
    resp.raise_for_status()
    data = resp.json()
    tool_use_blocks = [b for b in data.get("content", []) if b.get("type") == "tool_use"]
    text_blocks = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
    print("Text:", "".join(text_blocks))
    print("Tool calls:", tool_use_blocks)
    return data


# ---------------------------------------------------------------------------
# Claude Chat-Compatible Format
# ---------------------------------------------------------------------------

def claude_chat_compatible_with_thinking(prompt: str = "Hello!", model: str = "claude-sonnet-4-20250514"):
    """Claude chat-compatible format with thinking."""
    client = create_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        stream=True,
        max_tokens=16000,
        thinking={"type": "enabled", "budget_tokens": 10240},
    )
    content = ""
    for chunk in response:
        if chunk.choices[0].delta.content:
            content += chunk.choices[0].delta.content
            print(chunk.choices[0].delta.content, end="", flush=True)
    print()
    return content


# ---------------------------------------------------------------------------
# Gemini Native Format (raw requests)
# ---------------------------------------------------------------------------

def gemini_native_text(prompt: str, model: str = "gemini-2.5-pro"):
    """Gemini native format text generation via raw requests."""
    import requests

    headers = {
        "Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}",
        "Content-Type": "application/json",
    }
    payload = {
        "systemInstruction": {"parts": [{"text": "You are a helpful assistant."}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 1, "topP": 1},
    }
    resp = requests.post(
        f"{os.getenv('LINGXI_BASE_URL')}/v1beta/models/{model}:generateContent",
        headers=headers,
        json=payload,
    )
    resp.raise_for_status()
    data = resp.json()
    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    text = "".join(p.get("text", "") for p in parts)
    print("Gemini native:", text)
    return data


def gemini_native_with_image(image_path: str, prompt: str = "Describe this image", model: str = "gemini-2.5-pro"):
    """Gemini native format with inline image."""
    import requests

    headers = {
        "Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}",
        "Content-Type": "application/json",
    }
    path = Path(image_path)
    b64 = base64.b64encode(path.read_bytes()).decode("utf-8")
    mime = f"image/{path.suffix.lstrip('.')}" if path.suffix else "image/png"
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": prompt},
                    {"inlineData": {"mimeType": mime, "data": b64}},
                ],
            }
        ],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1024},
    }
    resp = requests.post(
        f"{os.getenv('LINGXI_BASE_URL')}/v1beta/models/{model}:generateContent",
        headers=headers,
        json=payload,
    )
    resp.raise_for_status()
    data = resp.json()
    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    text = "".join(p.get("text", "") for p in parts)
    print("Gemini vision:", text)
    return data


def gemini_native_structured_output(prompt: str = "Give me a person's info", model: str = "gemini-2.5-pro"):
    """Gemini native format with structured output."""
    import requests

    headers = {
        "Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}",
        "Content-Type": "application/json",
    }
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"},
                },
                "required": ["name", "age"],
            },
        },
    }
    resp = requests.post(
        f"{os.getenv('LINGXI_BASE_URL')}/v1beta/models/{model}:generateContent",
        headers=headers,
        json=payload,
    )
    resp.raise_for_status()
    data = resp.json()
    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    text = "".join(p.get("text", "") for p in parts)
    print("Gemini structured:", text)
    return data


# ---------------------------------------------------------------------------
# Gemini Chat-Compatible Format
# ---------------------------------------------------------------------------

def gemini_chat_compatible(prompt: str = "Who are you?", model: str = "gemini-2.5-pro"):
    """Gemini chat-compatible format via OpenAI SDK."""
    client = create_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        top_p=1,
        stream=False,
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content


def gemini_chat_compatible_with_image(image_url: str, prompt: str = "What is this image?", model: str = "gemini-1.5-pro-latest"):
    """Gemini chat-compatible vision."""
    client = create_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ],
        temperature=0.9,
        max_tokens=400,
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content


# ---------------------------------------------------------------------------
# Responses API (OpenAI)
# ---------------------------------------------------------------------------

def responses_api_basic(prompt: str = "Hello", model: str = "gpt-4.1"):
    """OpenAI Responses API basic call."""
    import requests

    headers = {
        "Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "input": [{"role": "user", "content": prompt}],
    }
    resp = requests.post(
        f"{os.getenv('LINGXI_BASE_URL')}/v1/responses",
        headers=headers,
        json=payload,
    )
    resp.raise_for_status()
    data = resp.json()
    output_text = ""
    for item in data.get("output", []):
        if item.get("type") == "message":
            for c in item.get("content", []):
                if c.get("type") == "output_text":
                    output_text += c.get("text", "")
    print("Responses API:", output_text)
    return data


def responses_api_with_reasoning(prompt: str = "Explain relativity", model: str = "gpt-5.1"):
    """OpenAI Responses API with reasoning control."""
    import requests

    headers = {
        "Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "input": [{"role": "user", "content": prompt}],
        "reasoning": {"effort": "high"},
    }
    resp = requests.post(
        f"{os.getenv('LINGXI_BASE_URL')}/v1/responses",
        headers=headers,
        json=payload,
    )
    resp.raise_for_status()
    data = resp.json()
    output_text = ""
    for item in data.get("output", []):
        if item.get("type") == "message":
            for c in item.get("content", []):
                if c.get("type") == "output_text":
                    output_text += c.get("text", "")
    print("Responses reasoning:", output_text)
    return data


def responses_api_with_web_search(prompt: str = "Latest AI news today", model: str = "gpt-4.1-2025-04-14"):
    """OpenAI Responses API with web search."""
    import requests

    headers = {
        "Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "tools": [{"type": "web_search_preview"}],
        "input": prompt,
    }
    resp = requests.post(
        f"{os.getenv('LINGXI_BASE_URL')}/v1/responses",
        headers=headers,
        json=payload,
    )
    resp.raise_for_status()
    data = resp.json()
    output_text = ""
    for item in data.get("output", []):
        if item.get("type") == "message":
            for c in item.get("content", []):
                if c.get("type") == "output_text":
                    output_text += c.get("text", "")
    print("Responses web search:", output_text)
    return data


def responses_api_with_function_calling(prompt: str = "Get the horoscope for Aquarius", model: str = "gpt-4.1"):
    """OpenAI Responses API with function calling."""
    import requests

    headers = {
        "Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "input": [{"role": "user", "content": prompt}],
        "tools": [
            {
                "type": "function",
                "name": "get_horoscope",
                "description": "Get today's horoscope for an astrological sign.",
                "parameters": {
                    "type": "object",
                    "properties": {"sign": {"type": "string"}},
                    "required": ["sign"]
                }
            }
        ],
        "tool_choice": "auto",
    }
    resp = requests.post(
        f"{os.getenv('LINGXI_BASE_URL')}/v1/responses",
        headers=headers,
        json=payload,
    )
    resp.raise_for_status()
    data = resp.json()
    for item in data.get("output", []):
        if item.get("type") == "function_call":
            print("Function call:", item.get("name"), item.get("arguments"))
        elif item.get("type") == "message":
            for c in item.get("content", []):
                if c.get("type") == "output_text":
                    print("Message:", c.get("text"))
    return data


def responses_api_multiturn(prompt1: str = "Hello", prompt2: str = "Tell me more", model: str = "gpt-4.1"):
    """OpenAI Responses API multi-turn conversation."""
    import requests

    headers = {
        "Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}",
        "Content-Type": "application/json",
    }
    first = requests.post(
        f"{os.getenv('LINGXI_BASE_URL')}/v1/responses",
        headers=headers,
        json={"model": model, "input": [{"role": "user", "content": prompt1}]},
    ).json()

    second = requests.post(
        f"{os.getenv('LINGXI_BASE_URL')}/v1/responses",
        headers=headers,
        json={
            "model": model,
            "input": [{"role": "user", "content": prompt2}],
            "previous_response_id": first["id"],
        },
    )
    second.raise_for_status()
    data = second.json()
    output_text = ""
    for item in data.get("output", []):
        if item.get("type") == "message":
            for c in item.get("content", []):
                if c.get("type") == "output_text":
                    output_text += c.get("text", "")
    print("Multi-turn response:", output_text)
    return data


# ---------------------------------------------------------------------------
# Legacy Completions
# ---------------------------------------------------------------------------

def legacy_completion(prompt: str = "你好,", model: str = "gpt-3.5-turbo-instruct"):
    """Legacy prompt-based completion API."""
    client = create_client()
    response = client.completions.create(
        model=model,
        prompt=prompt,
        max_tokens=30,
        temperature=0,
    )
    print(response.choices[0].text)
    return response.choices[0].text


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Run a minimal sanity check
    chat_completion("Hello, Lingxi! Introduce yourself in one sentence.")
