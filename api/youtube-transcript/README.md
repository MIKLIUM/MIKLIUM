## YouTube Transcription API

### Navigation

- [YouTube Transcription API](#youtube-transcription-api)
    - [Navigation](#navigation)
    - [About YouTube Transcription](#about-youtube-transcription)
    - [Request Body](#request-body)
        - [GET Method](#get-method)
        - [POST Method](#post-method)
    - [API Responses](#api-responses)
        - [Success](#success)
        - [Error](#error)
    - [What Services Does This API Use?](#what-services-does-this-api-use-)

### About YouTube Transcription

### Request Body

Link: `https://miklium.vercel.app/api/youtube-transcript`

| Parameter | Required | Description |
| :--- | :--- | :--- |
| `url` | Yes | Link to the YouTube video from which you want to extract the text. |

#### GET Method

`GET https://miklium.vercel.app/api/youtube-transcript?url=URL**`

**Important!** The link to the YouTube video should be URL-encoded!

**Request Link Example:**

`https://miklium.vercel.app/api/youtube-transcript?url=https://youtu.be/Qz8u00pX738`

#### POST Method

`POST https://miklium.vercel.app/api/youtube-transcript`

```json
{"url":URL}
```

**Request Body Example (JSON):**

```json
{"url":"https://youtu.be/Qz8u00pX738"}
```

### API Responses

#### Success


#### Error

### What Services Does This API Use?