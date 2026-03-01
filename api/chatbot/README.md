# Chatbot API Documentation

## Navigation

- [Chatbot API Documentation](#chatbot-api-documentation)
    - [Navigation](#navigation)
    - [About MIKLIUM Chatbot API](#about-miklium-chatbot-api)
    - [Request Body](#request-body)
        - [GET Method](#get-method)
        - [POST Method](#post-method)
    - [Response Stacking](#response-stacking)
    - [Bot Personalities](#bot-personalities)
    - [Supported Topics](#supported-topics)
    - [Code Examples](#code-examples)
    - [API Responses](#api-responses)
        - [Success](#success)
        - [Error](#error)

## About MIKLIUM Chatbot API

**A lightweight, rule-based chatbot.** This API provides a conversational interface that can answer questions about MIKLIUM, its APIs, documentation, community, and more. It is designed to work on low-compute devices and delivers quick, deterministic responses with no external dependencies.

Unlike a single-match bot, MIKLIUM Chatbot supports **response stacking** — when your message touches multiple topics (e.g. a greeting *and* a question about the APIs), the chatbot can intelligently combine matching responses into one rich reply.

## Request Body

Link: `https://miklium.vercel.app/api/chatbot`

| Parameter | Required | Type | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `message` | Yes | String | — | The user's message to the chatbot |
| `response_stacking` | No | Integer (0 – 100) | `4` | How many matched topic responses to combine in the reply |
| `personality` | No | String | `miklium` | The personality of the bot (`miklium`, `personalityless`, `male`, `female`, `all`) |

### GET Method

`https://miklium.vercel.app/api/chatbot?message=Paste Your message here`

> [!IMPORTANT]
> For GET Method the message should be URL-encoded!

**Request Link Examples:**
* `https://miklium.vercel.app/api/chatbot?message=Hello%2C%20how%20do%20I%20use%20the%20Python%20Sandbox%3F`
* `https://miklium.vercel.app/api/chatbot?message=Hi%2C%20how%20are%20you%3F&response_stacking=2&personality=male`

### POST Method

`https://miklium.vercel.app/api/chatbot`

```javascript
{
  "message": "Hello, how do I use the Python Sandbox?",
  "response_stacking": 4,
  "personality": "miklium"
}
```

## Response Stacking

`response_stacking` is an optional integer parameter (**0 – 100**, default **`4`**) that controls how many pattern-matched responses are combined into the final reply.

| Value | Behaviour |
| :--- | :--- |
| `0` | Only the **first** matching response is returned (classic single-match mode) |
| `1` – `99` | Up to **N + 1** matched responses are joined into one reply |
| `100` | All matching responses are combined (maximum verbosity) |

**How it works:** The chatbot scans your message against every topic pattern in order. Each time a pattern matches, one randomly-chosen response for that topic is added to the list. When the list reaches `response_stacking + 1` entries (or all patterns have been checked), the collected responses are joined with a space and returned as a single string.

**Example — `response_stacking: 2` with message `"Hey, how are you? Tell me about the APIs"`:**

```javascript
// Request
{
  "message": "Hey, how are you? Tell me about the APIs",
  "response_stacking": 2
}

// Response (three matched topics combined)
{
  "response": "Hey there! Welcome to MIKLIUM. What can I do for you? Running at full capacity and feeling fantastic! What can I do for you? All MIKLIUM APIs are free and require no API key. Current offerings: Python Sandbox, Search, YouTube Transcript, Apple Shortcuts Info, and Chatbot."
}
```

## Bot Personalities

The `personality` parameter allows you to change the bot's tone and response style.

| Personality | Alias | Description |
| :--- | :--- | :--- |
| **MIKLIUM** | `miklium` | The default assistant. Helpful, professional, and knowledgeable about MIKLIUM. |
| **Personalityless** | `personalityless`| A cold, logical bot. Minimalist and formal. Focused on pure data. |
| **General Male** | `male` | A friendly guy in his early 20s. Casual tone, uses "yo", "vibing", etc. |
| **General Female** | `female` | A friendly girl in her early 20s. Warm tone, uses emojis and casual language. |
| **All** | `all` | A hybrid mode that uses all response sets. This is the **most intelligent mode** as it pulls from every knowledge base. |

Each personality has its own unique set of pattern responses and fallbacks. The "All" mode is particularly powerful as it combines the strengths (and variety) of every single personality into one.

## Supported Topics

The chatbot recognises a wide range of topics out of the box:

| Topic | Example phrases |
| :--- | :--- |
| Greetings | hello, hi, hey, good morning, howdy |
| How are you | how are you, you doing okay, are you well |
| Capabilities | what can you do, how can you help |
| APIs overview | apis, what do you offer, what is available |
| Documentation | docs, documentation, how to use, guide |
| Python Sandbox | python, sandbox, run code, code execution |
| Search API | search, web search, find, queries |
| YouTube Transcript | youtube, transcript, captions, subtitles |
| Apple Shortcuts | shortcut, icloud, routinehub, automation |
| Chatbot API | chatbot, chat api, this api, bot api |
| Response Stacking | response stacking, stacking, stacked response |
| GitHub / OSS | github, open source, contribute, pull request |
| Community / Support | discord, help, support, bug, issue |
| About MIKLIUM | what is miklium, who made you, about miklium |
| Pricing | free, cost, price, subscription |
| Rate Limits | rate limit, quota, throttle |
| Error Handling | error, 500, 400, bad request, not working |
| Authentication | auth, api key, token, bearer |
| Request Format | json, body, content-type, endpoint |
| Versioning | version, update, changelog, release |
| Deployment | deploy, vercel, serverless, self-host |
| Language / SDK | sdk, npm, curl, fetch, javascript, python |
| Examples | example, sample, demo, getting started |
| Thanks | thank you, appreciate, awesome, great |
| Goodbye | bye, goodbye, see you, take care |
| Jokes | joke, funny, lol, humor |
| Time / Date | time, date, today, clock |
| Weather | weather, temperature, forecast |

## Code Examples

### JavaScript (Fetch)
```javascript
const url = 'https://miklium.vercel.app/api/chatbot';
const data = {
  message: "Hello, how do I use the Python Sandbox?",
  response_stacking: 4,
  personality: "miklium"
};

fetch(url, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(data)
})
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
```

### Python (Requests)
```python
import requests

url = "https://miklium.vercel.app/api/chatbot"
data = {
    "message": "Hello, how do I use the Python Sandbox?",
    "response_stacking": 4,
    "personality": "miklium"
}

try:
    response = requests.post(url, json=data)
    response.raise_for_status()
    print(response.json())
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
```

### cURL
```bash
curl -X POST https://miklium.vercel.app/api/chatbot \
     -H "Content-Type: application/json" \
     -d '{
           "message": "Hello, how do I use the Python Sandbox?",
           "response_stacking": 4,
           "personality": "miklium"
         }'
```

## API Responses

### Success

**Response structure:**
| Parameter | Value |
| :--- | :--- |
| `response` | `String`, The chatbot's response text (may be multiple sentences if stacking > 0) |

**Success response example (no stacking):**
```javascript
{
  "response": "You can find our full API documentation at APIDOCS.html. It covers all endpoints and usage examples."
}
```

**Success response example (stacking = 2, greeting + how-are-you combined):**
```javascript
{
  "response": "Hi! Great to see you here. Ask me anything about MIKLIUM! All systems green! I'm here and ready to assist."
}
```

### Error

| Parameter | Value |
| :--- | :--- |
| `error` | `String`, Error message |

**Error response example:**
```javascript
{
  "error": "Missing 'message' field"
}
```
