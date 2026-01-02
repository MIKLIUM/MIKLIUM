# Search API Documentation

## Navigation

- [Search API Documentation](#search-api-documentation)
    - [Navigation](#navigation)
    - [About MIKLIUM Search API](#about-miklium-search-api)
    - [Request Body](#request-body)
        - [GET Method](#get-method)
        - [POST Method](#post-method)
    - [API Responses](#api-responses)
        - [Success](#success)
        - [Error](#error)
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
| `maxSmallSnippets`| No | Number | The number of short information for each request (by default 5) |
| `maxLargeSnippets` | No | Number | The number of long information for each request (by default 2) |
| `maxLargeSnippetSymbols` | No | Number | Maximum number of characters for one long information (by default 4500) |

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
