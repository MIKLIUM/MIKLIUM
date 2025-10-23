# YouTube Transcription API Documentation

## Navigation

- [YouTube Transcription API Documentation](#youtube-transcription-api-documentation)
    - [Navigation](#navigation)
    - [About MIKLIUM YouTube Transcription API](#about-miklium-youtube-transcription-api)
    - [Request Body](#request-body)
        - [GET Method](#get-method)
        - [POST Method](#post-method)
    - [API Responses](#api-responses)
        - [Success](#success)
        - [Error](#error)
    - [What Services Does This API Use?](#what-services-does-this-api-use-)

## About MIKLIUM YouTube Transcription API

**Get text from a YouTube video in seconds using our API.** Also with the transcription of the video you will get the name of the channel and the title of the video. To work, you only need a link to a YouTube video.

> [!NOTE]
> This API works only with YouTube videos.

## Request Body

Link: `https://miklium.vercel.app/api/youtube-transcript`

| Parameter | Required | Description |
| :--- | :--- | :--- |
| `url` | Yes | Link to the YouTube video from which you want to extract the text. |

### GET Method

`https://miklium.vercel.app/api/youtube-transcript?url=Paste Your link here`

> [!IMPORTANT]
> For GET Method the link to the YouTube video should be URL-encoded!

**Request Link Example:**
`https://miklium.vercel.app/api/youtube-transcript?url=https://youtu.be/Qz8u00pX738`

### POST Method

`https://miklium.vercel.app/api/youtube-transcript`

```json
{
  "url": "Paste Your link here"
}
```

**Request Body Example (JSON):**
```json
{
  "url": "https://youtu.be/Qz8u00pX738"
}
```

## API Responses

### Success

| Parameter | Value |
| :--- | :--- |
| `success` | `true` |
| `channel` | `String`, YouTube channel name |
| `title` | `String`, Video title |
| `text` | `String`, Video transcription |

**Success response example:**
```json
{
  "success": true,
  "channel": "Apple",
  "title": "New things on the way from Apple",
  "text": "Voiceover: Want to see..."
}
```

### Error

| Parameter | Value |
| :--- | :--- |
| `success` | `false` |
| `error` | `String`, Error message |

**Error response example:**
```json
{
  "success": false,
  "error": "Invalid YouTube URL."
}
```

## What Services Does This API Use?

- [YouTube To Transcript](https://youtubetotranscript.com)