# MIKLIUM API Documentation

# Navigation
### Information
 - [MIKLIUM API Documentation](#miklium-api-documentation)
 - [Navigation](#navigation)
 - [About MIKLIUM APIs](#about-miklium-apis)
### APIs Documentations
 - [Python Sandbox API Documentation](#python-sandbox-api-documentation)
 - [Search API Documentation](#search-api-documentation)
 - [Apple Shortcuts Data API Documentation](#apple-shortcuts-data-api-documentation)
 - [YouTube Transcription API Documentation](#youtube-transcription-api-documentation)

# About MIKLIUM APIs

At MIKLIUM, we empower developers and users with high-quality, free APIs and software tools to help you build, innovate, and explore without limits. Here you will find detailed documentation for each of our APIs.

---
# Python Sandbox API Documentation

## Navigation
**[Back to MIKLIUM APIs navigation](#navigation)**


- [Python Sandbox API Documentation](#python-sandbox-api-documentation)
    - [Navigation](#navigation-1)
    - [About MIKLIUM Python Sandbox API](#about-miklium-python-sandbox-api)
    - [Request Body](#request-body)
        - [POST Method](#post-method)
    - [API Responses](#api-responses)
        - [Success](#success)
        - [Error](#error)
    - [Limitations](#limitations)
        - [Code Limitations](#code-limitations)
        - [Code Running and Output Limits:](#code-running-and-output-limits)

## About MIKLIUM Python Sandbox API

**Easily and quickly launch Python code.** Using this API, you can run Python code, configuring timeouts and inputs as needed for your code execution. Everything works without external dependencies.

_Python Sandbox was suggested for creation by [Elc29](https://github.com/TheCodeWan)._

## Request Body

Link: `https://miklium.vercel.app/api/python-sandbox`

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `code` | Yes | Text | Your Python code |
| `stdin` | No | Array | Inputs for your program |
| `timeout` | No | Number | Code execution time limit in seconds (by default `20`, maximum `40`, minimum `0.5`) |

### POST Method

`https://miklium.vercel.app/api/python-sandbox`

```javascript
{
  "code": "Paste Your Python code here",
  "stdin": ["Paste input here", "Another input…"] // Not necessarily
  "timeout": 0 // Number of seconds (Not necessarily)
}
```

**Request Body Examples (JSON):**

* Python code:
  ```python
  print('Hello World!')
  ```
  Request Body:
  ```javascript
  {
    "code": "print('Hello World!')"
  }
  ```

* Python code:
  ```python
  a, b = int(input()), int(input()) # For example, inputs are 2 and 6
  print(a, '+', b, '=', a+b)
  ```
  Request Body:
  ```javascript
  {
    "code": "a, b = int(input()), int(input())\nprint(a, '+', b, '=', a+b)",
    "stdin": [ 2, 6 ]
  }
  ```

## API Responses

### Success

**Response structure:**
| Parameter | Value |
| :--- | :--- |
| `success` | `true` |
| `exit_code` | `0` |
| `stdout` | `Text`, Python program output |
| `time_ms` | `Number`, Code execution time in milliseconds |

**Success response example:**
```javascript
{
  "success" : true,
  "exit_code" : 0,
  "stdout" : "5 + 6 = 11",
  "time_ms" : 18
}
```

### Error

**Server error:**
| Parameter | Value |
| :--- | :--- |
| `success` | `false` |
| `error` | `String`, Error message |

**Code running error:**
| Parameter | Value |
| :--- | :--- |
| `success` | `false` |
| `exit_code` | `Number`, Code of error |
| `stdout` | `Text`, Python program output before error |
| `time_ms` | `Number`, Code execution time in milliseconds |
| `error` | `Text`, Python error message |


**Error response examples:**
```javascript
{
  "success" : false,
  "error" : "Blocked: os — not allowed in sandbox"
}
```
```javascript
{
  "success" : false,
  "stdout" : "",
  "exit_code" : 1,
  "time_ms" : 22,
  "error" : "Runtime error: Traceback (most recent call last):\n  line 1, in <module>\nImportError: cannot import name 'products' from 'itertools' (unknown location). Did you mean: 'product'?"
}
```

## Limitations

Unfortunately, the Python Sandbox is not designed to run very complex or potentially dangerous code, so it has several limitations.

### Code Limitations:

* Maximum number of lines of code:`15 000`
* Blocked modules that cannot be imported:
  ```python
  "os", "subprocess", "shutil", "pathlib", "glob", "tempfile" # File system
  "socket", "urllib", "requests", "httpx", "http", "aiohttp" # Network
  "ftplib", "smtplib", "imaplib", "poplib" # Mail protocols
  "multiprocessing", "threading", "signal", "asyncio" # Concurrency
  "ctypes", "cffi", "mmap" # Low-level operations
  "pickle", "shelve", "marshal" # Unsafe serialization
  "importlib", "code", "codeop" # Dynamic imports
  "webbrowser", "antigravity", "turtle" # GUI and browser
  "gc", "resource", "atexit", "io" # System resources
  ```
* Third-party modules cannot be imported
* Blocked build-in functions:
  ```python
  open() # File read or write
  exec() # Execute arbitrary code
  eval() # Evaluate strings as code
  compile() # Compile code
  breakpoint() # Debugging
  __import__() # Dynamic import (intercepted)
  exit() # Exit program
  quit() # Exit program
  ```
* Blocked Dunder Attributes (sandbox escape prevention):
  ```python
  __subclasses__ # Get subclasses (for RCE)
  __globals__ # Access global variables
  __builtins__ # Access built-in functions
  __code__ # Access bytecode
  __bases__ # Parent classes
  __mro__ # Method Resolution Order
  ```

### Code Running and Output Limits:

* Maximum Python program output: `10 000` characters
* Maximum Python code error message: `7 000` characters
* Maximum timeout: `40` seconds (can be configured in Request Body)
* Maximum of memory usage (RAM): `64` MB
* Maximum of recursion (then function calls itself) depth: `200` levels. Example of recursion:
  ```python
  # Factorial calculator

  def factorial(n):
    if n <= 1:
      return 1
    return n * factorial(n - 1) # Function calls itself

  print(factorial(5))  # 120
  ```


---
# Search API Documentation

## Navigation
**[Back to MIKLIUM APIs navigation](#navigation)**


- [Search API Documentation](#search-api-documentation)
    - [Navigation](#navigation-2)
    - [About MIKLIUM Search API](#about-miklium-search-api)
    - [Request Body](#request-body-1)
        - [GET Method](#get-method)
        - [POST Method](#post-method-1)
    - [API Responses](#api-responses-1)
        - [Success](#success-1)
        - [Error](#error-1)
    - [Additional Information](#additional-information)
        - [Types of the Information](#types-of-the-information)
        - [Choosing the Right Information Format](#choosing-the-right-information-format)
    - [What Services Does This API Use?](#what-services-does-this-api-use)

## About MIKLIUM Search API

**Get information from the Internet on your request in a convenient format.** You can also configure how much data you need to receive and in what format. Our API uses the Yahoo Search engine and website scraping system.

## Request Body

Link: `https://miklium.vercel.app/api/search`

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `search` | Yes | Array | Search queries (maximum 3) |
| `maxSmallSnippets`| No | Number | The number of short information for each request (by default `5`) |
| `maxLargeSnippets` | No | Number | The number of long information for each request (by default `2`) |
| `maxLargeSnippetSymbols` | No | Number | Maximum number of characters for one long information (by default `4500`) |

### GET Method

`https://miklium.vercel.app/api/search?search=Paste Your query(queries) here`

If you want to write several requests at once (maximum 3), connect them with `~`. If you want to add additional parameters, write them through `&`.

> [!IMPORTANT]
> For GET Method the search requests should be URL-encoded!

**Request Link Examples:**
* `https://miklium.vercel.app/api/search?search=iPhone%20Air`
* `https://miklium.vercel.app/api/search?search=iPhone%20Air~iPhone%2017%20Pro&maxSmallSnippets=3&maxLargeSnippets=0`

### POST Method

`https://miklium.vercel.app/api/search`

```javascript
{
  "search": ["Paste Your query here", "If You need more requests at a time, add new objects to the list (maximum 3)"],
  "maxSmallSnippets": 0, // Number (Not necessarily)
  "maxLargeSnippets": 0, // Number (Not necessarily)
  "maxLargeSnippetSymbols": 0 // Number (Not necessarily)
}
```

**Request Body Examples (JSON):**
```javascript
{
  "search": ["iPhone Air"]
}
```
```javascript
{
  "search": ["iPhone Air", "iPhone 17 Pro"],
  "maxSmallSnippets": 3,
  "maxLargeSnippets": 0
}
```

## API Responses

### Success

**General response:**
| Parameter | Value |
| :--- | :--- |
| `success` | `true` |
| `results` | `Array with Dictionaries`, Search results |

**Components of `results` elements:**
| Parameter | Value |
| :--- | :--- |
| `query` | `String`, The request to which the information was found |
| `symbols` | `Number`, The number of characters that this information contains |
| `url` | `String`, Link to the source of the information |
| `type` | `String: short OR long`, Type of the information |
| `snippet` | `String`, The information itself |

**Success response example:**
```javascript
{
  "success": true,
  "results": [
    {
      "symbols": 194,
      "query": "iPhone Air ",
      "url": "https://en.wikipedia.org/wiki/Iphone_air",
      "type": "short",
      "snippet": "iPhone Air is..."
    },
    {
      "symbols": 4500,
      "query": "iPhone 17 Pro Max",
      "url": "https://www.pcmag.com/reviews/apple-iphone-17-pro-max",
      "type": "long",
      "snippet": "iPhone 17 Pro is…"
    }
  ]
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
  "error": "Invalid or missing 'search' parameter."
}
```

## Additional Information

### Types of the Information

As you have already noticed, the API returns two types of information: `short` and `long`. How are they different? Information marked `short` is obtained from a brief description of the site from the search engine. And the `long` information is already the full text from the site.

### Choosing the Right Information Format

* You can change the amount of information issued and its type using parameters maxSmallSnippets` (the number of short information for each request (by default 5), `maxLargeSnippets` (the number of long information for each request (by default 2) and `maxLargeSnippetSymbols` (maximum number of characters for one long information (by default 4500).

* By setting the parameter `maxSmallSnippets` to 0, you will receive only information with `long` type, full information from sites. And by setting `maxLargeSnippets` to 0, you will only receive information with `short` type, brief information.

* The number behind the parameters `maxSmallSnippets` and `maxLargeSnippets` is responsible for the amount of relevant information for each request. For example, if we have two quires  in `search`, we set `maxSmallSnippets` to 2, and `maxLargeSnippets` to 1. Thus, 4 short information and 2 long will be found: 2 short and 1 long for each request.

* The parameter `maxLargeSnippetSymbols` is responsible for the maximum number of characters in long information (by default 4500). If the limit is increased, the long information will be cut off.

## What Services Does This API Use?

- [Yahoo Search](https://search.yahoo.com)


---
# Apple Shortcuts Data API Documentation

## Navigation
**[Back to MIKLIUM APIs navigation](#navigation)**


- [Apple Shortcuts Data API Documentation](#apple-shortcuts-data-api-documentation)
    - [Navigation](#navigation-3)
    - [About MIKLIUM Apple Shortcuts Data API](#about-miklium-apple-shortcuts-data-api)
    - [Request Body](#request-body-2)
        - [GET Method](#get-method-1)
        - [POST Method](#post-method-2)
    - [API Responses](#api-responses-2)
        - [Success](#success-2)
        - [Error](#error-2)
    - [What Services Does This API Use?](#what-services-does-this-api-use-1)

## About MIKLIUM Apple Shortcuts Data API

**Get detailed information about Apple Shortcut from its link quickly and conveniently.** Using this API, you can get data such as the name of the shortcut, the date of creation of the link to it, the links to download the signed `.shortcut` file, `.plist` file, the shortcut icon and much more. Our “shortcut data scraper” uses the iCloud API system and RoutineHub API for [RoutineHub](https://routinehub.co/) (place where you can search for beautiful and incredible shortcuts and share yours projects) integration.

## Request Body

Link: `https://miklium.vercel.app/api/shortcut-info`

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `url` | Yes | Text | Shortcut link (iCloud links, RoutineHub links and direct download RoutineHub links are supported) |

### GET Method

`https://miklium.vercel.app/api/shortcut-info?url=Paste Your link here`

> [!IMPORTANT]
> For GET Method the link to shortcut should be URL-encoded!

**Request Link Examples:**
* `https://miklium.vercel.app/api/shortcut-info?url=https://www.icloud.com/shortcuts/dbd68fde729740b2a7218a177808655f`
* `https://miklium.vercel.app/api/shortcut-info?url=https://routinehub.co/download/56215/`
* `https://miklium.vercel.app/api/shortcut-info?url=https://routinehub.co/shortcut/18431/`

### POST Method

`https://miklium.vercel.app/api/shortcut-info`

```javascript
{
  "url": "Paste Your link here"
}
```

**Request Body Examples (JSON):**
```javascript
{
  "url": "https://routinehub.co/shortcut/18431/"
}
```
```javascript
{
  "url": "https://www.icloud.com/shortcuts/dbd68fde729740b2a7218a177808655f"
}
```

## API Responses

### Success

```javascript
{
  "success": true,
  "inputType": "…", // The type of the URL that was entered as an input
  "shortcutLinks": {
    "iCloudLink": "…", // iCloud link to download shortcut, if it was found, or null
    "routineHubLink": "…", // RoutineHub link to shortcut, if it was found, or null
    "routineHubDirectLink": "…" // RoutineHub direct download link to shortcut, if it was found, or null
  },
  "shortcutData": {
    "name": "…", // Shotcut name
    "dateOfSharing": {
      "readable": "…", // Date of creation of a shortcut link in a readable format
      "asInShortcuts": "…", // Date of creation of a shortcut link in format displayed in the “Shortcuts” app
      "iso8601": "…", // Date of creation of a shortcut link in ISO 8601 format
      "rfc2822": "…", // Date of creation of a shortcut link in RFC 2822 format
      "timestamp": 0 // Date of creation of a shortcut link in timestamp format
    },
    "icon": {
      "colorId": 255, // ID of the background color of the shortcut icon
      "glyphId": 61989, // ID of the glyph of the shortcut icon
      "size": {
        "mb": 0.00, // Size of the .png shortcut icon in megabytes
        "kb": 0.00, // Size of the .png shortcut icon in kilobytes
        "bit": 0 // Size of the .png shortcut icon in bites
      },
      "downloadUrl": "…" // Link to download the .png shortcut icon
    },
    "signedShortcutFile": {
      "isSigned": true,
      "size": {
        "mb": 0.00, // Size of the signed .shortcut file in megabytes
        "kb": 0.00, // Size of the signed .shortcut file in kilobytes
        "bit": 0 // Size of the signed .shortcut file in bites
      },
      "downloadUrl": "…" // Link to download the signed .shortcut file
    },
    "plistShortcutFile": {
      "size": {
        "mb": 0.00, // Size of the .plist file in megabytes
        "kb": 0.00, // Size of the .plist file in kilobytes
        "bit": 0 // Size of the .plist file in bites
      },
      "downloadUrl": "…" // Link to download the .plist file
    }
  }
}
```

**Success response example:**
```javascript
{
  "success": true,
  "inputType": "RoutineHub Link",
  "shortcutLinks": {
    "iCloudLink": "https://www.icloud.com/shortcuts/dbd68fde729740b2a7218a177808655f",
    "routineHubLink": "https://routinehub.co/shortcut/18431",
    "routineHubDirectLink": "https://routinehub.co/download/56215"
  },
  "shortcutData": {
    "name": "Nuvole AI",
    "dateOfSharing": {
      "readable": "October 21, 2025 at 10:34:17 AM (GMT)",
      "asInShortcuts": "October 21 2025",
      "iso8601": "2025-10-21T10:34:17.360Z",
      "rfc2822": "Tue, 21 Oct 2025 10:34:17 GMT",
      "timestamp": 1761042857360
    },
    "icon": {
      "colorId": 255,
      "glyphId": 61989,
      "size": {
        "mb": 0.04,
        "kb": 43.37,
        "bit": 44406
      },
      "downloadUrl": "https://cvws.icloud-content.com/…"
    },
    "signedShortcutFile": {
      "isSigned": true,
      "size": {
        "mb": 0.95,
        "kb": 970.73,
        "bit": 994025
      },
      "downloadUrl": "https://cvws.icloud-content.com/…"
    },
    "plistShortcutFile": {
      "size": {
        "mb": 2.71,
        "kb": 2779.88,
        "bit": 2846600
      },
      "downloadUrl": "https://cvws.icloud-content.com/…"
    }
  }
}
```

> [!IMPORTANT]
> Links to download files and icon image are temporary and are valid for about 7 hours.

### Error

| Parameter | Value |
| :--- | :--- |
| `success` | `false` |
| `error` | `String`, Error message |

**Error response example:**
```javascript
{
  "success": false,
  "error": "Invalid shortcut URL"
}
```

## What Services Does This API Use?

- iCloud Shortcuts Records API
- [RoutineHub API](https://github.com/mvan231/RoutineHubDocs/blob/main/README.md)


---
# YouTube Transcription API Documentation

## Navigation
**[Back to MIKLIUM APIs navigation](#navigation)**


- [YouTube Transcription API Documentation](#youtube-transcription-api-documentation)
    - [Navigation](#navigation-4)
    - [About MIKLIUM YouTube Transcription API](#about-miklium-youtube-transcription-api)
    - [Request Body](#request-body-3)
        - [GET Method](#get-method-2)
        - [POST Method](#post-method-3)
    - [API Responses](#api-responses-3)
        - [Success](#success-3)
        - [Error](#error-3)
    - [What Services Does This API Use?](#what-services-does-this-api-use-2)

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
