import json
import re
import random
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# ---------------------------------------------------------------------------
# Response stacking
# ---------------------------------------------------------------------------
# response_stacking controls how many pattern-matched responses are joined
# together into a single reply.
#
#   0  → only the first matching response (no stacking)
#   1  → up to 1 stacked response (same as 0 in practice; kept for symmetry)
#   N  → up to N matching responses are combined
#  100 → all matching responses are combined (maximum)
#
# The value is accepted as a request parameter and is clamped to [0, 100].
# ---------------------------------------------------------------------------
DEFAULT_RESPONSE_STACKING = 4

# ---------------------------------------------------------------------------
# Main rule-based knowledge base
# Each entry: (regex_pattern, [list of possible replies])
# Patterns are tested against the lower-cased user message in ORDER.
# All matches up to `response_stacking` are collected; their replies are
# picked randomly and joined with a space to form the final response.
# ---------------------------------------------------------------------------
RESPONSES = [
    # ── Greetings ────────────────────────────────────────────────────────────
    (r"\b(hello|hi|hey|howdy|sup|what'?s up|greetings|good (morning|afternoon|evening|day))\b", [
        "Hello! I'm the MIKLIUM Assistant. How can I help you today?",
        "Hey there! Welcome to MIKLIUM. What can I do for you?",
        "Hi! Great to see you here. Ask me anything about MIKLIUM!",
        "Greetings, traveler! How may I assist you with MIKLIUM today?",
        "Hey! I'm here and ready to help. What's on your mind?",
    ]),

    # ── How are you / wellbeing ──────────────────────────────────────────────
    (r"\b(how are you|how('?re| are) you doing|you doing|how do you feel|are you (ok|okay|good|well|alright))\b", [
        "I'm doing great, thanks for asking! I'm always ready to help.",
        "Running at full capacity and feeling fantastic! What can I do for you?",
        "As an AI I don't have feelings, but I'm operating perfectly — ask away!",
        "All systems green! I'm here and ready to assist.",
    ]),

    # ── What can you do / capabilities ──────────────────────────────────────
    (r"\b(what can you do|what do you (do|know|offer|support)|your (capabilities|features|skills)|help me with|how can you help)\b", [
        "I can answer questions about MIKLIUM, guide you through our APIs (Python Sandbox, Search, YouTube Transcript, Apple Shortcuts, Chatbot), and point you to docs and community resources.",
        "I know about all MIKLIUM APIs, how to use them, their parameters, and more. Try asking about a specific API!",
        "You can ask me about any MIKLIUM API, how to get started, where to find documentation, or how to contribute.",
    ]),

    # ── APIs overview ────────────────────────────────────────────────────────
    (r"\b(api|apis|what (do you|are|is) (offer|available|the apis?))\b", [
        "MIKLIUM offers several free, no-key-required APIs: Python Sandbox, Search, YouTube Transcript, Apple Shortcuts Data, and the Chatbot API you're talking to right now!",
        "We provide free APIs including: Python Sandbox (run code), Search (web search), YouTube Transcript (extract video text), Apple Shortcuts Data, and this Chatbot.",
        "All MIKLIUM APIs are free and require no API key. Current offerings: Python Sandbox, Search, YouTube Transcript, Apple Shortcuts Info, and Chatbot.",
    ]),

    # ── Documentation / docs ─────────────────────────────────────────────────
    (r"\b(documentation|docs|how (to|do i) use|api docs|api documentation|guide|tutorial|reference)\b", [
        "Full API documentation is available at APIDOCS.html on the MIKLIUM website. It covers every endpoint with examples.",
        "Check APIDOCS.html for comprehensive documentation — request/response schemas, examples, and limitations are all there.",
        "Our docs live at APIDOCS.html. You can also browse the /docs folder on the website for structured API guides.",
        "Need help getting started? Head to APIDOCS.html for step-by-step API documentation.",
    ]),

    # ── Python Sandbox ───────────────────────────────────────────────────────
    (r"\b(python|sandbox|python.?sandbox|run.?code|execute.?code|code.?execution)\b", [
        "The Python Sandbox API lets you run Python code safely in a sandboxed environment — no setup needed! POST your code to /api/python-sandbox.",
        "Our Python Sandbox supports stdin, custom timeouts (up to 40 s), and returns stdout, exit code, and execution time in milliseconds.",
        "Python Sandbox limitations: max 15 000 lines, 64 MB RAM, recursion depth 200, and certain dangerous modules (os, subprocess, etc.) are blocked for security.",
        "To use the Python Sandbox: POST `{\"code\": \"print('Hello!')\"}` to https://miklium.vercel.app/api/python-sandbox. That's it!",
        "The Python Sandbox is perfect for running quick code snippets, testing algorithms, or building educational tools — all with zero API keys.",
    ]),

    # ── Search API ───────────────────────────────────────────────────────────
    (r"\b(search|web.?search|search.?api|query|queries|search.?engine|find)\b", [
        "The MIKLIUM Search API lets you search the web without needing an API key. Supports up to 3 queries at once via POST to /api/search.",
        "Search results come in two types: `short` (brief snippets from the search engine) and `long` (full scraped text from the page). You control how many of each you get.",
        "Search API parameters: `search` (required, array of up to 3 queries), `maxSmallSnippets` (default 5), `maxLargeSnippets` (default 2), `maxLargeSnippetSymbols` (default 4500).",
        "We use Yahoo Search under the hood for our Search API, combined with a web-scraping layer for long-form results.",
        "Need just quick blurbs? Set `maxLargeSnippets: 0`. Want only full-page content? Set `maxSmallSnippets: 0`.",
    ]),

    # ── YouTube Transcript ───────────────────────────────────────────────────
    (r"\b(youtube|transcript|video.?text|caption|subtitles|yt|youtu\.?be)\b", [
        "The YouTube Transcript API extracts text from any YouTube video. Just POST the video URL to /api/youtube-transcript.",
        "YouTube Transcript supports optional `removeTimestamps` (boolean) and `includeInfo` (boolean) params to get video title, channel, views, likes, and more.",
        "Using the YouTube Transcript API with `includeInfo: true` returns the video title, channel name, subscriber count, view/like counts, hashtags, and duration.",
        "Transcript API is powered by the YouTube Scraper from Apify. It works with standard YouTube URLs and youtu.be short links.",
    ]),

    # ── Apple Shortcuts ──────────────────────────────────────────────────────
    (r"\b(shortcut|shortcuts|apple.?shortcut|icloud|routinehub|plist|automation)\b", [
        "The Apple Shortcuts Data API fetches metadata from iCloud shortcut links and RoutineHub links — name, creation date, icon, download URLs, and file sizes.",
        "Shortcuts API accepts iCloud links (icloud.com/shortcuts/...), RoutineHub shortcut pages, and RoutineHub direct download links.",
        "Shortcut icon download URLs and file download links are temporary and expire after ~7 hours, so cache them if you need them long-term.",
        "The Apple Shortcuts API uses the iCloud Shortcuts Records API and the RoutineHub API under the hood.",
    ]),

    # ── Chatbot API ──────────────────────────────────────────────────────────
    (r"\b(chatbot|chat.?bot|chat.?api|this.?api|you.?api|bot.?api)\b", [
        "I'm the MIKLIUM Chatbot API! I'm a lightweight, rule-based assistant living at /api/chatbot. You can query me via GET or POST.",
        "The Chatbot API accepts a `message` field and an optional `response_stacking` integer (0–100). Stacking lets multiple matched responses be combined into one reply.",
        "Fun fact: you can set `response_stacking` to a higher number to get richer, combined answers when your message matches multiple topics!",
    ]),

    # ── Response stacking ────────────────────────────────────────────────────
    (r"\b(response.?stacking|stack(ing)?|stacked.?response|multiple.?response)\b", [
        "`response_stacking` (0–100) controls how many matched responses are joined together. 0 = only the first match, 100 = all matches combined.",
        "With `response_stacking` set to say 3, if your message matches 3 different topics (e.g. greeting + 'how are you' + 'apis'), all three responses are combined.",
        "Response stacking is a unique MIKLIUM Chatbot feature. Set it high for verbose, multi-topic answers; keep it at 0 for focused single-topic replies.",
    ]),

    # ── GitHub / open source ─────────────────────────────────────────────────
    (r"\b(github|git|open.?source|source.?code|contribute|fork|pull.?request|pr|repo|repository)\b", [
        "MIKLIUM is fully open source! You can find, fork, and contribute to our code on GitHub.",
        "We love contributions! Check out CONTRIBUTING.md in the repo for guidelines — make sure test.py passes before opening a PR.",
        "Our GitHub repo holds all API source code, documentation, and the web frontend. Stars and PRs are always welcome!",
        "Found a bug or have a feature idea? Open an issue on GitHub and we'll take a look.",
    ]),

    # ── Discord / community / support ────────────────────────────────────────
    (r"\b(discord|community|help|support|chat|forum|ask|question|issue|bug|problem)\b", [
        "Join our Discord community for real-time support, discussions, and updates!",
        "The best places for help are our Discord server and GitHub Issues.",
        "Encountering an issue? Open a GitHub Issue with details and we'll get back to you.",
        "We have an active community — feel free to ask questions, share projects, and give feedback on Discord.",
    ]),

    # ── About MIKLIUM ────────────────────────────────────────────────────────
    (r"\b(who (are|made|built|is) (you|miklium)|what is miklium|about miklium|tell me about|miklium project|why miklium)\b", [
        "MIKLIUM is a project dedicated to providing free, high-quality APIs and developer tools — no API keys, no sign-ups, no barriers.",
        "We empower developers by removing friction: every MIKLIUM API is free and open to use immediately.",
        "MIKLIUM was built to make powerful tools accessible to everyone, from students to professional developers.",
        "Our mission is simple: great tooling should be free. That's the MIKLIUM philosophy.",
    ]),

    # ── Pricing / cost / free ────────────────────────────────────────────────
    (r"\b(free|cost|price|pricing|pay|paid|subscription|plan|charge|money|fee)\b", [
        "All MIKLIUM APIs are completely free! No payment, no subscription, no API key required.",
        "MIKLIUM is 100% free to use. We believe great developer tools shouldn't cost anything.",
        "There are no pricing tiers, credits, or paywalls — every API is free for everyone.",
    ]),

    # ── Rate limits / limits ─────────────────────────────────────────────────
    (r"\b(rate.?limit|limit|quota|throttle|max.?request|request.?limit|too many request)\b", [
        "MIKLIUM doesn't advertise hard rate limits, but please use the APIs responsibly and don't spam endpoints.",
        "For heavy usage, consider caching responses on your end to reduce unnecessary API calls.",
        "If you're hitting errors frequently, it may be due to upstream service limits. Check our GitHub Issues for known issues.",
    ]),

    # ── Error handling ───────────────────────────────────────────────────────
    (r"\b(error|500|400|bad.?request|server.?error|fail|failure|broken|not.?work|doesn.?t.?work)\b", [
        "All MIKLIUM APIs return an `error` string in their JSON response when something goes wrong. Always check the HTTP status code too.",
        "A 400 error usually means a missing or invalid parameter. Double-check your request body against the documentation.",
        "If you're seeing 500 errors consistently, it may be an upstream issue. Report it on GitHub Issues with the request details.",
        "Tip: test your requests with the GET method first (using URL params) before switching to POST — it makes debugging easier.",
    ]),

    # ── Authentication / API keys ────────────────────────────────────────────
    (r"\b(auth|authentication|api.?key|key|token|secret|header|bearer|oauth)\b", [
        "Great news — MIKLIUM APIs require NO authentication! No API keys, tokens, or headers needed.",
        "Just send your request directly to the endpoint. No Authorization headers, no keys, no sign-up.",
        "Zero-auth is a core MIKLIUM principle. Every API is open and ready to use without credentials.",
    ]),

    # ── JSON / request format ────────────────────────────────────────────────
    (r"\b(json|request.?body|body|content.?type|format|payload|post.?request|get.?request|endpoint)\b", [
        "All MIKLIUM APIs accept JSON bodies for POST requests. Set Content-Type: application/json in your headers.",
        "Most APIs also support GET with URL query parameters — great for quick testing in your browser.",
        "POST body example for the Chatbot: `{\"message\": \"Hello!\", \"response_stacking\": 3}`.",
    ]),

    # ── Response format / output ─────────────────────────────────────────────
    (r"\b(response|output|result|return|data|json.?response)\b", [
        "All MIKLIUM APIs return JSON. Success responses include relevant data fields; error responses include an `error` string.",
        "Response shapes vary by API — check APIDOCS.html for the exact schema of each endpoint.",
    ]),

    # ── Versioning / updates ─────────────────────────────────────────────────
    (r"\b(version|versioning|v1|v2|update|changelog|release|new.?feature|latest)\b", [
        "MIKLIUM APIs are continuously improved. Keep an eye on our GitHub repo for new releases and changelogs.",
        "We don't currently version our API URLs — updates are applied in-place, with backward compatibility as a priority.",
        "Want to stay updated? Watch our GitHub repo or join the Discord for announcements.",
    ]),

    # ── Deployment / hosting ─────────────────────────────────────────────────
    (r"\b(deploy|hosting|vercel|server|serverless|self.?host|production|infra)\b", [
        "MIKLIUM APIs are deployed on Vercel using serverless functions — so they scale automatically.",
        "The entire MIKLIUM stack is open source: you can self-host it by deploying the repo to your own Vercel project.",
        "Vercel's serverless infrastructure means MIKLIUM APIs have near-zero cold start times and are globally distributed.",
    ]),

    # ── Language / SDK ───────────────────────────────────────────────────────
    (r"\b(language|sdk|library|package|npm|pip|curl|fetch|axios|javascript|js|typescript|ts|node)\b", [
        "MIKLIUM APIs are language-agnostic — use any HTTP client: fetch, axios, requests, curl, httpx, etc.",
        "No official SDK yet, but our APIs are simple enough that a few lines of `fetch` or `requests` is all you need.",
        "JavaScript example: `const res = await fetch('https://miklium.vercel.app/api/chatbot', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({message:'Hi!'})});`",
    ]),

    # ── Examples / getting started ───────────────────────────────────────────
    (r"\b(example|sample|demo|snippet|getting.?started|quick.?start|how.?to.?start|walk.?through)\b", [
        "Check APIDOCS.html for code examples in every API section — including GET and POST request samples.",
        "Quickest way to start: hit a GET endpoint in your browser! For example: https://miklium.vercel.app/api/chatbot?message=Hello",
        "The /docs folder on the MIKLIUM website has modular API guides with examples for each API.",
    ]),

    # ── Thanks / appreciation ────────────────────────────────────────────────
    (r"\b(thank|thanks|thank.?you|appreciate|ty|thx|cheers|great|awesome|nice|love it|perfect)\b", [
        "You're very welcome! Happy to help.",
        "Anytime! Let me know if there's anything else I can do.",
        "Happy to help! Come back whenever you have more questions.",
        "Glad I could assist! Feel free to ask anything else.",
        "That means a lot — enjoy MIKLIUM!",
    ]),

    # ── Goodbye ──────────────────────────────────────────────────────────────
    (r"\b(bye|goodbye|good.?bye|see.?you|later|take.?care|ciao|farewell|ttyl|gotta.?go)\b", [
        "Goodbye! Have a fantastic day!",
        "See you later! Feel free to come back whenever you need help.",
        "Bye! Thanks for visiting MIKLIUM — have a great one!",
        "Take care! We're always here when you need us.",
    ]),

    # ── Insults / negativity (graceful fallback) ─────────────────────────────
    (r"\b(stupid|dumb|hate|useless|terrible|worst|awful|bad.?bot|horrible)\b", [
        "I'm sorry to hear that! I'm always trying to improve. Share feedback on our GitHub — it really helps.",
        "Ouch! Let me know what I can do better. Open an issue on GitHub and we'll look into it.",
        "Fair enough — I'm still learning! Your feedback on GitHub would help me get better.",
    ]),

    # ── Jokes / fun ──────────────────────────────────────────────────────────
    (r"\b(joke|funny|laugh|humor|humour|lol|haha|meme|fun)\b", [
        "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
        "I told a joke about APIs once... but nobody got the response. 😄",
        "What do you call a snake that builds things? A boa constructor! 🐍",
        "Here to help AND entertain! But mostly help — do you have a real question for me?",
    ]),

    # ── Time / date (self-aware edge case) ───────────────────────────────────
    (r"\b(time|date|today|day|clock|when|current.?time)\b", [
        "I don't have access to real-time clock data — I'm a stateless API! Check your device for the current time.",
        "As a serverless function I don't keep track of time, but your device should have that covered!",
    ]),

    # ── Weather ──────────────────────────────────────────────────────────────
    (r"\b(weather|temperature|rain|sun|snow|forecast|climate)\b", [
        "I'm focused on MIKLIUM APIs and can't check the weather. For live weather data, try a service like OpenWeather!",
        "Weather isn't my specialty — but you could use the MIKLIUM Search API to look it up!",
    ]),
]

# ---------------------------------------------------------------------------
# Fallback ELIZA-style responses when no pattern matches
# ---------------------------------------------------------------------------
ELIZA_RESPONSES = [
    "Interesting! Could you tell me more about that?",
    "I'm not sure I follow — can you rephrase or give more detail?",
    "That's a good point. Let me know how I can help further.",
    "I don't have a specific answer for that, but try asking about our APIs or check the docs!",
    "Hmm, I'm not sure about that one. Try asking about Python Sandbox, Search, YouTube Transcript, Apple Shortcuts, or the Chatbot API!",
    "I didn't quite catch that — could you rephrase? Or maybe ask about a specific MIKLIUM API?",
    "I specialise in MIKLIUM topics. Want to know about our APIs, docs, GitHub, or community?",
    "Good question! Though I'm not sure I have an answer. Try the GitHub Issues or Discord for more help.",
]


def get_response(user_input: str, response_stacking: int = 0) -> str:
    """Return a chatbot reply for *user_input*.

    response_stacking (0–100):
        0  → return the reply for only the first matching pattern.
        N  → collect up to N+1 matching patterns and join their replies.
        The function always returns at least one response.
    """
    # Clamp to valid range
    response_stacking = max(0, min(100, int(response_stacking)))

    text = user_input.lower()

    matched_replies = []
    for pattern, options in RESPONSES:
        if re.search(pattern, text):
            matched_replies.append(random.choice(options))
            # +1 because stacking=0 still gives 1 response
            if len(matched_replies) >= response_stacking + 1:
                break

    if matched_replies:
        return " ".join(matched_replies)

    # No pattern matched — use ELIZA fallback
    return random.choice(ELIZA_RESPONSES)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        params = parse_qs(parsed_path.query)
        message = params.get('message', [None])[0]

        if not message:
            self._send_json(400, {"error": "Missing 'message' query parameter"})
            return

        stacking_raw = params.get('response_stacking', ['0'])[0]
        try:
            stacking = int(stacking_raw)
        except (ValueError, TypeError):
            stacking = DEFAULT_RESPONSE_STACKING

        response_text = get_response(message, stacking)
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

        response_text = get_response(message, stacking)
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
