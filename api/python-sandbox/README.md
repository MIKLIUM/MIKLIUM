# Python Sandbox API Documentation

## Navigation

- [Python Sandbox API Documentation](#python-sandbox-api-documentation)
    - [Navigation](#navigation)
    - [About MIKLIUM Python Sandbox API](#about-miklium-python-sandbox-api)
    - [Request Body](#request-body)
        - [POST Method](#post-method)
    - [Code Examples](#code-examples)
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

## Code Examples

### JavaScript (Fetch)
```javascript
const url = 'https://miklium.vercel.app/api/python-sandbox';
const data = {
  code: "print('Hello from MIKLIUM!')\n",
  timeout: 10
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

url = "https://miklium.vercel.app/api/python-sandbox"
data = {
    "code": "print('Hello from MIKLIUM!')\n",
    "timeout": 10
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
curl -X POST https://miklium.vercel.app/api/python-sandbox \
     -H "Content-Type: application/json" \
     -d '{
           "code": "print('\''Hello from MIKLIUM!'\'')\n",
           "timeout": 10
         }'
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
  "posix", "nt", "posixpath", "ntpath", "genericpath", "pwd", "grp", "fcntl", "termios", "tty", "pty" # Low-level system
  "_posixsubprocess", "_signal" # Low-level process
  "_io" # Low-level backend
  "_frozen_importlib", "_frozen_importlib_external", "zipimport", "_imp" # Import system internals
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
