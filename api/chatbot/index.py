import json
import re
import random
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Import personalities
from personalities import miklium, personalityless, male, female

# ---------------------------------------------------------------------------
# Response stacking
# ---------------------------------------------------------------------------
DEFAULT_RESPONSE_STACKING = 4

def get_response(user_input: str, response_stacking: int = 4, personality: str = "miklium") -> str:
    """Return a chatbot reply for *user_input*.

    response_stacking (0–100):
        0  → return the reply for only the first matching pattern.
        N  → collect up to N+1 matching patterns and join their replies.
        The function always returns at least one response.

    personality: "miklium", "personalityless", "male", "female", or "all".
    """
    # Clamp to valid range
    response_stacking = max(0, min(100, int(response_stacking)))
    personality = personality.lower()

    # Determine response and fallback lists
    current_responses = []
    current_fallbacks = []

    if personality == "miklium":
        current_responses = miklium.RESPONSES
        current_fallbacks = miklium.FALLBACK
    elif personality == "personalityless":
        current_responses = personalityless.RESPONSES
        current_fallbacks = personalityless.FALLBACK
    elif personality == "male":
        current_responses = male.RESPONSES
        current_fallbacks = male.FALLBACK
    elif personality == "female":
        current_responses = female.RESPONSES
        current_fallbacks = female.FALLBACK
    elif personality == "all":
        # Mix everyone for maximum intelligence
        current_responses = (miklium.RESPONSES + personalityless.RESPONSES + 
                             male.RESPONSES + female.RESPONSES)
        current_fallbacks = (miklium.FALLBACK + personalityless.FALLBACK + 
                             male.FALLBACK + female.FALLBACK)
    else:
        # Fallback to miklium if personality is not recognized
        current_responses = miklium.RESPONSES
        current_fallbacks = miklium.FALLBACK

    text = user_input.lower()

    matched_replies = []
    for pattern, options in current_responses:
        if re.search(pattern, text):
            matched_replies.append(random.choice(options))
            # +1 because stacking=0 still gives 1 response
            if len(matched_replies) >= response_stacking + 1:
                break

    if matched_replies:
        return " ".join(matched_replies)

    # No pattern matched — use correct fallback
    return random.choice(current_fallbacks)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        params = parse_qs(parsed_path.query)
        message = params.get('message', [None])[0]

        if not message:
            self._send_json(400, {"error": "Missing 'message' query parameter"})
            return

        stacking_raw = params.get('response_stacking', [str(DEFAULT_RESPONSE_STACKING)])[0]
        try:
            stacking = int(stacking_raw)
        except (ValueError, TypeError):
            stacking = DEFAULT_RESPONSE_STACKING

        personality = params.get('personality', ["miklium"])[0]

        response_text = get_response(message, stacking, personality)
        self._send_json(200, {"response": response_text})

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if not content_length:
            self._send_json(400, {"error": "Missing body"})
            return

        try:
            body_bytes = self.rfile.read(content_length)
            body = json.loads(body_bytes)
            message = body.get('message', '').strip()
        except Exception:
            self._send_json(400, {"error": "Invalid JSON"})
            return

        if not message:
            self._send_json(400, {"error": "Missing 'message' field"})
            return

        stacking = body.get('response_stacking', DEFAULT_RESPONSE_STACKING)
        try:
            stacking = int(stacking)
        except (ValueError, TypeError):
            stacking = DEFAULT_RESPONSE_STACKING

        personality = body.get('personality', "miklium")

        response_text = get_response(message, stacking, personality)
        self._send_json(200, {"response": response_text})

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def _send_json(self, status, data):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self._cors()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def log_message(self, *a):
        pass
