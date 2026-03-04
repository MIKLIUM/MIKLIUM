import json
import re
import random
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from personalities import miklium, personalityless, male, female

DEFAULT_RESPONSE_STACKING = 4

PERSONALITY_MAP = {
    "miklium": (miklium, "RESPONSES", "FALLBACK"),
    "personalityless": (personalityless, "RESPONSES", "FALLBACK"),
    "male": (male, "RESPONSES", "FALLBACK"),
    "female": (female, "RESPONSES", "FALLBACK"),
}


def get_response(user_input: str, response_stacking: int = 4, personality: str = "miklium") -> str:
    response_stacking = max(0, min(100, int(response_stacking)))
    personality = personality.lower()

    if personality == "all":
        current_responses = (miklium.RESPONSES + personalityless.RESPONSES +
                             male.RESPONSES + female.RESPONSES)
        current_fallbacks = (miklium.FALLBACK + personalityless.FALLBACK +
                             male.FALLBACK + female.FALLBACK)
    elif personality in PERSONALITY_MAP:
        mod = PERSONALITY_MAP[personality][0]
        current_responses = mod.RESPONSES
        current_fallbacks = mod.FALLBACK
    else:
        print(f"Unknown personality requested: {personality}, falling back to miklium")
        current_responses = miklium.RESPONSES
        current_fallbacks = miklium.FALLBACK

    text = user_input.lower()

    matched_replies = []
    for pattern, options in current_responses:
        if re.search(pattern, text):
            matched_replies.append(random.choice(options))
            if len(matched_replies) >= response_stacking + 1:
                break

    if matched_replies:
        return " ".join(matched_replies)

    return random.choice(current_fallbacks)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        params = parse_qs(parsed_path.query)
        message = params.get('message', [None])[0]

        if not message:
            print("GET: missing message parameter")
            self._send_json(400, {"success": False, "error": "Missing 'message' query parameter"})
            return

        stacking_raw = params.get('response_stacking', [str(DEFAULT_RESPONSE_STACKING)])[0]
        try:
            stacking = int(stacking_raw)
        except (ValueError, TypeError):
            print(f"GET: invalid response_stacking value: {stacking_raw}")
            stacking = DEFAULT_RESPONSE_STACKING

        personality = params.get('personality', ["miklium"])[0]

        try:
            response_text = get_response(message, stacking, personality)
            self._send_json(200, {"success": True, "response": response_text})
        except Exception as e:
            print(f"GET: get_response failed: {type(e).__name__}: {e}")
            self._send_json(500, {"success": False, "error": "Internal server error"})

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if not content_length:
            print("POST: empty request body")
            self._send_json(400, {"success": False, "error": "Missing body"})
            return

        try:
            body_bytes = self.rfile.read(content_length)
            body = json.loads(body_bytes)
        except json.JSONDecodeError as e:
            print(f"POST: JSON parse failed: {e}")
            self._send_json(400, {"success": False, "error": "Invalid JSON"})
            return
        except Exception as e:
            print(f"POST: body read failed: {type(e).__name__}: {e}")
            self._send_json(400, {"success": False, "error": "Invalid request body"})
            return

        message = body.get('message', '')
        if isinstance(message, str):
            message = message.strip()

        if not message:
            print("POST: missing message field")
            self._send_json(400, {"success": False, "error": "Missing 'message' field"})
            return

        stacking = body.get('response_stacking', DEFAULT_RESPONSE_STACKING)
        try:
            stacking = int(stacking)
        except (ValueError, TypeError):
            print(f"POST: invalid response_stacking value: {stacking}")
            stacking = DEFAULT_RESPONSE_STACKING

        personality = body.get('personality', "miklium")

        try:
            response_text = get_response(message, stacking, personality)
            self._send_json(200, {"success": True, "response": response_text})
        except Exception as e:
            print(f"POST: get_response failed: {type(e).__name__}: {e}")
            self._send_json(500, {"success": False, "error": "Internal server error"})

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def _send_json(self, status, data):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def log_message(self, *a):
        pass
