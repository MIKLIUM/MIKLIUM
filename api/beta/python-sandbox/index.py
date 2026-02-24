import json
import sys
import subprocess
import tempfile
import os
import re
import time
from http.server import BaseHTTPRequestHandler

MAX_CODE_LENGTH = 25_000
MAX_STDOUT = 50_000
MAX_STDERR = 25_000
MAX_TIMEOUT = 50
DEFAULT_TIMEOUT = 20
MAX_MEMORY_MB = 128
MAX_RECURSION = 150

BLOCKED_MODULES = [
    "os", "subprocess", "shutil", "pathlib", "glob", "tempfile",
    "socket", "urllib", "requests", "httpx", "http", "aiohttp",
    "ftplib", "smtplib", "imaplib", "poplib",
    "multiprocessing", "threading", "signal", "asyncio",
    "ctypes", "cffi", "mmap",
    "pickle", "shelve", "marshal",
    "importlib", "code", "codeop",
    "webbrowser", "antigravity", "turtle",
    "gc", "resource", "atexit", "io",
]

BLOCKED_BUILTINS = [
    "open", "exec", "eval", "compile", "breakpoint",
    "__import__", "exit", "quit",
]

BLOCKED_DUNDERS = [
    "__subclasses__", "__globals__", "__builtins__",
    "__code__", "__bases__", "__mro__",
]

ALL_BLOCKED = (
    [(rf"\b{re.escape(m)}\b", m) for m in BLOCKED_MODULES]
    + [(rf"\b{re.escape(b)}\s*\(", b) for b in BLOCKED_BUILTINS]
    + [(re.escape(d), d) for d in BLOCKED_DUNDERS]
)

COMPILED = [(re.compile(p), name) for p, name in ALL_BLOCKED]

TMP_FILE_RE = re.compile(r'File "/tmp/[^"]+", ')


def strip_strings(code):
    r = re.sub(r'"""[\s\S]*?"""', '""', code)
    r = re.sub(r"'''[\s\S]*?'''", "''", r)
    r = re.sub(r'"[^"\n]*"', '""', r)
    r = re.sub(r"'[^'\n]*'", "''", r)
    r = re.sub(r"#.*$", "", r, flags=re.MULTILINE)
    return r


def check(code):
    clean = strip_strings(code)
    return [name for pat, name in COMPILED if pat.search(clean)]


def clean_stderr(text):
    return TMP_FILE_RE.sub("", text)


WRAPPER = '''
import sys, builtins
try:
    import resource
    _mem = {max_memory} * 1024 * 1024
    try: resource.setrlimit(resource.RLIMIT_AS, (_mem, _mem))
    except: pass
    try: resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))
    except: pass
    try: resource.setrlimit(resource.RLIMIT_NPROC, (0, 0))
    except: pass
except:
    pass
sys.setrecursionlimit({max_recursion})
_blocked = set({blocked_set})
_orig = __import__
def _si(n, *a, **k):
    if n.split(".")[0] in _blocked:
        raise ImportError(f"'{{n}}' is blocked")
    return _orig(n, *a, **k)
builtins.__import__ = _si
builtins.open = None
builtins.exec = None
builtins.eval = None
builtins.compile = None
builtins.breakpoint = None
{code}
'''


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        return self._json(405, {"success": False, "error": "Only POST method is supported"})

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        if not length:
            return self._json(400, {"success": False, "error": "Empty body"})

        try:
            body = json.loads(self.rfile.read(length))
        except json.JSONDecodeError:
            return self._json(400, {"success": False, "error": "Invalid JSON"})

        code = body.get("code", "")
        stdin_list = body.get("stdin", [])
        timeout = min(max(0.5, body.get("timeout", DEFAULT_TIMEOUT)), MAX_TIMEOUT)

        if not code or not isinstance(code, str):
            return self._json(400, {"success": False, "error": "Missing 'code'"})

        if len(code) > MAX_CODE_LENGTH:
            return self._json(400, {"success": False, "error": "Code too long"})

        if not isinstance(stdin_list, list):
            return self._json(400, {"success": False, "error": "'stdin' must be an array"})

        stdin_data = "\n".join(str(item) for item in stdin_list)

        blocked = check(code)
        if blocked:
            names = ", ".join(blocked)
            return self._json(403, {
                "success": False,
                "error": f"Blocked: {names} — not allowed in sandbox",
            })

        script = WRAPPER.format(
            code=code,
            blocked_set=repr(BLOCKED_MODULES),
            max_memory=MAX_MEMORY_MB,
            max_recursion=MAX_RECURSION,
        )
        start = time.perf_counter()

        tmp = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, dir="/tmp") as f:
                f.write(script)
                tmp = f.name

            result = subprocess.run(
                [sys.executable, "-u", tmp],
                input=stdin_data,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd="/tmp",
                env={"PATH": "/usr/bin:/bin", "HOME": "/tmp", "PYTHONDONTWRITEBYTECODE": "1"},
            )
            ms = round((time.perf_counter() - start) * 1000, 2)

            stderr_clean = clean_stderr(result.stderr[:MAX_STDERR]) if result.stderr else None

            if result.returncode != 0:
                error_msg = "Runtime error"
                if stderr_clean:
                    error_msg += ": " + stderr_clean.strip()
                return self._json(200, {
                    "success": False,
                    "error": error_msg,
                    "stdout": result.stdout[:MAX_STDOUT],
                    "exit_code": result.returncode,
                    "time_ms": ms,
                })

            return self._json(200, {
                "success": True,
                "stdout": result.stdout[:MAX_STDOUT],
                "exit_code": result.returncode,
                "time_ms": ms,
            })
        except subprocess.TimeoutExpired:
            ms = round((time.perf_counter() - start) * 1000, 2)
            return self._json(200, {
                "success": False,
                "error": f"Timed out after {timeout}s",
                "stdout": "",
                "exit_code": -1,
                "time_ms": ms,
            })
        except Exception as e:
            return self._json(200, {
                "success": False,
                "error": "Code execution error: " + str(e),
            })
        finally:
            if tmp:
                try:
                    os.unlink(tmp)
                except:
                    pass

    def _json(self, status, data):
        body = json.dumps(data, ensure_ascii=False, default=str).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def log_message(self, *a):
        pass