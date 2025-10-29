# Apple Shortcuts Data API Documentation

## Navigation

- [Apple Shortcuts Data API Documentation](#apple-shortcuts-data-api-documentation)
    - [Navigation](#navigation)
    - [About MIKLIUM Apple Shortcuts Data API](#about-miklium-apple-shortcuts-data-api)
    - [Request Body](#request-body)
        - [GET Method](#get-method)
        - [POST Method](#post-method)
    - [API Responses](#api-responses)
        - [Success](#success)
        - [Error](#error)
    - [What Services Does This API Use?](#what-services-does-this-api-use-)

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