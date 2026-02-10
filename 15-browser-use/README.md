# Building Computer Use Agents with Browser-Use and Playwright
[![Browser Use](./images/lesson-15-thumbnail.png)](https://youtu.be/your-video-link)

This lesson explores how to build AI agents that can interact with the web just like a human does. By combining **Playwright** for browser automation and **Browser-Use** for AI-driven navigation, we can create agents that perform complex tasks like searching for travel deals, gathering data, or automating form submissions.

## Introduction

This lesson will cover:

• **Understanding Computer Use Agents**: How agents can control software interfaces.
• **Browser-Use Framework**: Using the Browser-Use library to orchestrate browser interactions.
• **Vision-Based Navigation**: Leveraging GPT-4 Vision to "see" and understand web pages.
• **Structured Data Extraction**: Converting unstructured web content into structured Pydantic models.

## Learning Goals

After completing this lesson, you will know how to:

• **Set up a Browser-Use Agent** with Playwright integration.
• **Implement an AI Agent** that can navigate to websites and perform search queries.
• **Extract structured data** (like prices and ratings) from dynamic web pages using vision models.
• **Build a price comparison tool** that finds the cheapest options on a site like Airbnb.

## What are Computer Use Agents?

Computer Use Agents (CUA) are AI systems designed to interact with computer interfaces (GUIs) rather than just processing text. While traditional agents might call APIs, CUAs can:
- Click buttons and type text.
- Scroll and navigate through pages.
- Interpret visual elements (layouts, images, icons).
- Handle dynamic content that APIs might not expose.

In this lesson, we focus on **Browser Use**, a specific type of CUA that operates within a web browser.

## The Architecture

We use a powerful combination of tools:

1.  **Playwright**: A robust library for browser automation. It handles the low-level "actor" tasks: launching the browser, clicking coordinates, and managing pages.
2.  **Browser-Use**: A higher-level framework that bridges the LLM with Playwright. It translates natural language instructions (e.g., "Find the cheapest hotel") into browser actions.
3.  **Azure OpenAI (GPT-4 Vision)**: The "brain" and "eyes" of the agent. It analyzes screenshots of the page to understand the layout and content, then decides what to do next.

## Example: Airbnb Price Finder

The code sample for this lesson (`15-browser-user.ipynb`) demonstrates a real-world use case: finding the cheapest Airbnb in Stockholm.

### Workflow:
1.  **Navigate**: The agent launches Chrome and goes to Airbnb.com.
2.  **Search**: It types "Stockholm, Sweden" and submits the search.
3.  **Extract**: Using vision, it identifies listing cards and extracts details like price, rating, and title into a structured format.
4.  **Compare**: The agent logic analyzes the extracted data to highlight the best deal.

## Best Practices

*   **Hybrid Approach**: Use "Agents" for exploration (handling dynamic pop-ups or unknown layouts) and "Actors" (direct code) for precise, repetitive tasks.
*   **Visual Debugging**: Always take screenshots or run in `headed` mode (visible browser) during development to see what the agent sees.
*   **Structured Output**: Use Pydantic models to ensure the data you extract is reliable and typed, rather than just raw text strings.

## Next Steps

Try extending the example to:
- Search for flights instead of hotels.
- Login to a site (handling authentication securely).
- Scrape data across multiple pages (pagination).
