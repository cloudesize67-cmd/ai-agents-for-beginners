# Creating Local AI Agents with SLMs

![Local Agents](../images/lesson-17-thumbnail.png)

Cloud-based LLMs are powerful, but sometimes you need agents that run entirely on your own device—for privacy, cost savings, or offline capabilities. This lesson explores building agents using Small Language Models (SLMs) and local inference tools.

## Introduction

This lesson will cover:

• **Small Language Models (SLMs)**: Understanding efficient models like Phi-3, Llama-3-8B, and Mistral.
• **Local Inference Engines**: Using tools like Ollama, LM Studio, and ONNX Runtime.
• **Privacy and Latency**: The benefits of processing data locally.
• **Hybrid Architectures**: Combining local responsiveness with cloud intelligence when needed.

## Learning Goals

After completing this lesson, you will know how to:

• **Run an SLM locally** using Ollama or ONNX.
• **Connect your Agent framework** (Semantic Kernel, AutoGen) to a local model endpoint.
• **Build a private document Q&A agent** that never sends data to the cloud.
• **Optimize prompts** for smaller, less capable models.

## Why Local Agents?

1.  **Privacy**: Sensitive data (medical, legal, personal) stays on the device.
2.  **Cost**: No per-token API fees. You pay only for the hardware electricity.
3.  **Latency**: Instant responses without network round-trips (dependent on hardware).
4.  **Offline Access**: Agents work without an internet connection.

## Tools of the Trade

### Phi-3
Microsoft's family of open, highly capable small language models. They achieve performance comparable to much larger models while being efficient enough to run on a laptop or even a phone.

### Ollama
A popular tool for simplifying the setup and running of local LLMs. It provides an OpenAI-compatible API, making it easy to swap out `gpt-4` for `llama3` or `phi3` in your code.

```bash
ollama run phi3
```

### Semantic Kernel & Local Models
Most agent frameworks support local endpoints. You simply configure the `baseUrl` to point to your local server (e.g., `http://localhost:11434` for Ollama).

## Practical Exercise

*(Coming Soon: Building a local email summarizer using Phi-3 and Ollama)*
