# Chatbot API Documentation

## Navigation

- [Chatbot API Documentation](#chatbot-api-documentation)
    - [Navigation](#navigation)
    - [About MIKLIUM Chatbot API](#about-miklium-chatbot-api)
    - [Request Body](#request-body)
        - [GET Method](#get-method)
        - [POST Method](#post-method)
    - [API Responses](#api-responses)
        - [Success](#success)
        - [Error](#error)

## About MIKLIUM Chatbot API

**A lightweight, rule-based chatbot.** This API provides a 1990s-style conversational interface that can answer questions about MIKLIUM, its APIs, and documentation. It is designed to work on low-compute devices and provides quick, deterministic responses.

## Request Body

Link: `https://miklium.vercel.app/api/chatbot`

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `message` | Yes | String | The user's message to the chatbot |

### GET Method

`https://miklium.vercel.app/api/chatbot?message=Paste Your message here`

> [!IMPORTANT]
> For GET Method the message should be URL-encoded!

**Request Link Example:**
* `https://miklium.vercel.app/api/chatbot?message=Hello%2C%20how%20do%20I%20use%20the%20Python%20Sandbox%3F`

### POST Method

`https://miklium.vercel.app/api/chatbot`

```javascript
{
  "message": "Hello, how do I use the Python Sandbox?"
}
```

## API Responses

### Success

**Response structure:**
| Parameter | Value |
| :--- | :--- |
| `response` | `String`, The chatbot's response text |

**Success response example:**
```javascript
{
  "response": "You can find our full API documentation at APIDOCS.html. It covers all endpoints and usage examples."
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
