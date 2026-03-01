import json
import re
import random
from http.server import BaseHTTPRequestHandler

RESPONSES = [
    (r"hello|hi|hey", [
        "Hello! I am the MIKLIUM Assistant. How can I help you today?",
        "Hi there! What can I do for you?",
        "Greetings! How may I assist you with MIKLIUM today?"
    ]),
    (r"api|apis|what (do you|is) (offer|available)", [
        "MIKLIUM offers free APIs including Python Sandbox, Search, YouTube Transcription, and Apple Shortcuts Data. Which one would you like to know more about?",
        "We have several free APIs available: Search, Python Sandbox, YouTube Transcript, and Apple Shortcuts info."
    ]),
    (r"documentation|docs|how (to|do I) use", [
        "You can find our full API documentation at APIDOCS.html. It covers all endpoints and usage examples.",
        "Check out the docs at APIDOCS.html for help with our APIs."
    ]),
    (r"github|git|source|code", [
        "MIKLIUM is fully open source! You can find our code on GitHub.",
        "Our projects are hosted on GitHub. Feel free to explore and contribute!"
    ]),
    (r"discord|chat|community|help|support", [
        "Join our Discord community for support and discussions!",
        "If you need help, our Discord server is the best place to ask.",
        "You can find support via GitHub Issues or our Discord channel."
    ]),
    (r"who (are|made) (you|miklium)|what is miklium", [
        "MIKLIUM is a project dedicated to providing free, high-quality APIs and tools for everyone, no keys required.",
        "We empower developers by removing barriers like API keys and sign-ups."
    ]),
    (r"python|sandbox", [
        "Our Python Sandbox API allows you to run Python code safely in a controlled environment.",
        "The Python Sandbox is one of our most popular APIs. You can try it out today!"
    ]),
    (r"search", [
        "The MIKLIUM Search API allows you to perform web searches without needing an API key.",
        "Need to search the web? Our Search API is free and easy to integrate."
    ]),
    (r"youtube|transcript", [
        "Our YouTube Transcription API can extract text from any YouTube video.",
        "You can use our YouTube API to get transcripts for videos quickly."
    ]),
    (r"shortcut|apple", [
        "We provide an API to get information from Apple Shortcuts links.",
        "The Apple Shortcuts Data API is great for automation enthusiasts."
    ]),
    (r"thank", [
        "You're very welcome!",
        "Anytime! Let me know if you need anything else.",
        "Happy to help!"
    ]),
    (r"bye|goodbye", [
        "Goodbye! Have a great day!",
        "See you later! Feel free to come back if you have more questions.",
        "Bye! Thanks for visiting MIKLIUM."
    ])
]

ELIZA_RESPONSES = [
    "Tell me more about that.",
    "I see. And how does that make you feel?",
    "Can you elaborate on that?",
    "Why do you say that?",
    "Interesting. Please, go on.",
    "Does that bother you?",
    "I am not sure I understand completely. Can you explain?"
]

def get_response(user_input):
    user_input = user_input.lower()
    
    for pattern, options in RESPONSES:
        if re.search(pattern, user_input):
            return random.choice(options)
            
    # If no keywords matched, use a generic ELIZA response
    return random.choice(ELIZA_RESPONSES)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        from urllib.parse import urlparse, parse_qs
        parsed_path = urlparse(self.path)
        params = parse_qs(parsed_path.query)
        message = params.get('message', [None])[0]

        if not message:
            self._send_json(400, {"error": "Missing 'message' query parameter"})
            return

        response_text = get_response(message)
        self._send_json(200, {"response": response_text})

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if not content_length:
            self._send_json(400, {"error": "Missing body"})
            return

        try:
            body = json.loads(self.rfile.read(content_length))
            message = body.get('message', '').strip()
        except Exception:
            self._send_json(400, {"error": "Invalid JSON"})
            return

        if not message:
            self._send_json(400, {"error": "Missing 'message' field"})
            return

        response_text = get_response(message)
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
        self.wfile.write(json.dumps(data).encode())

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
