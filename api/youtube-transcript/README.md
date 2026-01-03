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
    - [What Services Does This API Use?](#what-services-does-this-api-use)

## About MIKLIUM YouTube Transcription API

**Get text from a YouTube video in seconds using our API.** Also with the transcription of the video you can get additional details such as title, channel name, stats, etc. To work, you only need a link to a YouTube video.

> [!NOTE]
> This API works only with YouTube videos.

## Request Body

Link: `https://miklium.vercel.app/api/youtube-transcript`

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `url` | Yes | Text | Link to the YouTube video from which you want to extract the text |
| `removeTimestamps` | No | Boolean | Whether to remove timestamps from the transcription (by default `false`) |
| `includeInfo` | No | Boolean | Whether to include additional video details such as title, channel name, stats and more (by default `false`) |

### GET Method

`https://miklium.vercel.app/api/youtube-transcript?url=Paste Your link here`

If you want to add additional parameters, write them through `&`.

> [!IMPORTANT]
> For GET Method the link to the YouTube video should be URL-encoded!

**Request Link Example:**
* `https://miklium.vercel.app/api/youtube-transcript?url=https://youtu.be/Qz8u00pX738`
* `https://miklium.vercel.app/api/youtube-transcript?url=https://youtu.be/dQw4w9WgXcQ&removeTimestamps=true&includeInfo=true`

### POST Method

`https://miklium.vercel.app/api/youtube-transcript`

```javascript
{
  "url": "Paste Your link here",
  "removeTimestamps": true, // Boolean (Not necessarily)
  "includeInfo": true // Boolean (Not necessarily)
}
```

**Request Body Example (JSON):**
```javascript
{
  "url": "https://youtu.be/Qz8u00pX738"
}
```
```javascript
{
  "url": "https://youtu.be/dQw4w9WgXcQ",
  "removeTimestamps": true,
  "includeInfo": true
}
```

## API Responses

### Success

**General response:**
| Parameter | Value |
| :--- | :--- |
| `success` | `true` |
| `transcript` | `String`, Video transcription |
| `info` | `Dictionary`, Video info (if `includeInfo` is `true` |

**Structure of `info`:**
```javascript
{
  "video": {
    "id": "...", // Video ID
    "title": "...", // Video title
    "description": "...", // Video description
    "duration": "00:00:00", // Video duration in 'HH:MM:SS' format
    "date": "…", // Date the video was posted in ISO 8601 format
    "hashtags": [
        "#…",
        "#..."
    ] // Video hashtags
  },
  "channel": {
    "name": "...", // Channel name
    "username": "...", // Channel username
    "subscribers": 0 // Subscribers count
  },
  "stats": {
    "views": 0, // Views count
    "likes": 0, // Likes count
    "comments": 0 // Comments count
  }
}
```

**Success response example:**
```javascript
{
  "success": true,
  "transcript": "Voiceover: Want to see something gorgeous…",
  "info": {
    "video": {
      "id": "Qz8u00pX738",
      "title": "New things on the way from Apple",
      "description": "Woah. Here’s your guide to some of the big announcements from this year’s Worldwide Developers Conference...",
      "duration": "00:02:13",
      "date": "2025-06-09T18:41:34.000Z",
      "hashtags": [
        "#LiquidGlass",
        "#AppleEvent",
        "#WWDC25"
      ]
    },
    "channel": {
      "name": "Apple",
      "username": "Apple",
      "subscribers": 20600000
    },
    "stats": {
      "views": 1673530,
      "likes": 41000,
      "comments": 0
    }
  }
}
```

### Error

| Parameter | Value |
| :--- | :--- |
| `success` | `false` |
| `error` | `String`, Error message |

**Error response example:**
```javascript
{
  "success": false,
  "error": "Invalid YouTube URL."
}
```

## What Services Does This API Use?

- [YouTube Scraper (Created by @Streamers at Apify)](https://apify.com/streamers/youtube-scraper)