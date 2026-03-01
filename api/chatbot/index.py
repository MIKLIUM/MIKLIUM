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
MIKLIUM_RESPONSES = [
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

    # ── Your name / identity ─────────────────────────────────────────────────
    (r"\b(what('?s| is) your (name|handle|alias)|who are you|introduce yourself|your name|call you)\b", [
        "I'm the MIKLIUM Assistant — a lightweight, rule-based chatbot built to answer your questions about MIKLIUM and its APIs.",
        "You can call me MIKLIUM Bot! I live at /api/chatbot and I'm here to help.",
        "My name is MIKLIUM Assistant. I'm a free, open-source chatbot — no ML required!",
        "I go by MIKLIUM Assistant. Think of me as your guide to all things MIKLIUM.",
    ]),

    # ── Compliments ──────────────────────────────────────────────────────────
    (r"\b(good bot|well done|clever|smart|impressive|you('?re| are) (good|great|amazing|cool|the best)|love you|you rock)\b", [
        "Aw, thanks! That really means a lot to a humble rule-based bot. 😊",
        "You're making me blush! Thanks — now how can I help you?",
        "Appreciate it! I'm always giving my best for MIKLIUM users.",
        "Thanks! High praise from a human. Now, is there something I can help you with?",
    ]),

    # ── Contributing ─────────────────────────────────────────────────────────
    (r"\b(contribut|how.?to.?help|add.?api|new.?api|submit|patch|contributing\.?md)\b", [
        "Want to contribute? Fork the repo on GitHub, make your changes, make sure test.py passes, then open a Pull Request!",
        "We welcome contributions of all kinds — new APIs, bug fixes, docs improvements. Check CONTRIBUTING.md for the full guide.",
        "To add a new API: fork the repo, add your endpoint under /api/, update APIDOCS.md, add tests to test.py, and open a PR.",
        "Check out CONTRIBUTING.md in the root of the repo — it has everything you need to get started as a contributor.",
    ]),

    # ── Testing ──────────────────────────────────────────────────────────────
    (r"\b(test|tests|test\.py|testing|unit.?test|run.?test|ci|passing|failing)\b", [
        "MIKLIUM has a test.py script in the root of the repo. Run it with `python3 test.py` to verify all APIs are working.",
        "All MIKLIUM API contributions must pass test.py before a PR can be merged. Make sure your changes don't break existing tests!",
        "The test suite covers every API endpoint via POST requests. If a test fails, check the error output and fix the issue before submitting.",
        "You can add your own API tests to test.py — just follow the existing pattern and add a new test block for your endpoint.",
    ]),

    # ── License ──────────────────────────────────────────────────────────────
    (r"\b(license|licence|mit|copyright|legal|terms|usage.?rights|intellectual.?property)\b", [
        "MIKLIUM is licensed under the MIT License — you can use, modify, and distribute it freely. Check LICENSE.md for details.",
        "Our code is MIT licensed, so you're free to fork, build on, and even commercialise it as long as you include the license.",
        "Full license info is in LICENSE.md at the root of the MIKLIUM GitHub repo.",
    ]),

    # ── Security ─────────────────────────────────────────────────────────────
    (r"\b(security|vulnerabilit|exploit|cve|secure|hack|attack|injection|xss|safe)\b", [
        "Security is important to us! If you discover a vulnerability, please report it via our SECURITY.md process — don't open a public issue.",
        "The Python Sandbox is sandboxed precisely to prevent security exploits — dangerous modules and built-ins are blocked.",
        "Found a security issue? Check SECURITY.md in the repo for the responsible disclosure process.",
        "We proactively block dangerous operations in the Python Sandbox (os, subprocess, eval, exec, etc.) to keep it safe for everyone.",
    ]),

    # ── Performance / speed ──────────────────────────────────────────────────
    (r"\b(fast|slow|speed|performance|latency|response.?time|millisecond|ms|quick|instant)\b", [
        "MIKLIUM APIs are deployed on Vercel's global edge network, so response times are typically very low no matter where you are.",
        "The Chatbot API is entirely rule-based — no model inference, no network calls — so it responds in milliseconds.",
        "For best performance, cache API responses on your end when the data doesn't change frequently (e.g. shortcut metadata).",
        "The Python Sandbox execution time is returned in the `time_ms` field so you can monitor your code's performance.",
    ]),

    # ── CORS / cross-origin ──────────────────────────────────────────────────
    (r"\b(cors|cross.?origin|access.?control|origin|preflight|options.?request|browser.?request)\b", [
        "All MIKLIUM APIs support CORS — you can call them directly from a browser with no proxy needed.",
        "CORS headers (Access-Control-Allow-Origin: *) are set on every response, so front-end apps can call MIKLIUM APIs directly.",
        "Preflight OPTIONS requests are handled automatically by all MIKLIUM API endpoints.",
    ]),

    # ── Featured projects / showcase ─────────────────────────────────────────
    (r"\b(featured|project|showcase|built.?with|example.?project|use.?case|who.?use|cool.?thing)\b", [
        "Check out FEATURED_PROJECTS.md in the repo to see cool things people have built using MIKLIUM APIs!",
        "Want your project featured? Build something cool with MIKLIUM and share it — we'd love to highlight it in FEATURED_PROJECTS.md.",
        "MIKLIUM APIs have been used for all kinds of creative projects. Browse FEATURED_PROJECTS.md for inspiration!",
    ]),

    # ── Roadmap / future features ────────────────────────────────────────────
    (r"\b(roadmap|future|plan|next|upcoming|coming.?soon|todo|what.?next|new.?api|feature.?request)\b", [
        "Check TODO.md in the repo for a peek at what's planned for MIKLIUM's future!",
        "We're always thinking about new APIs and improvements. Got a suggestion? Open a GitHub Issue with your idea!",
        "Future features are tracked in TODO.md and GitHub Issues. Feel free to upvote or comment on existing requests.",
        "Want a new API? Open a feature request issue on GitHub — if there's enough interest, we'll build it!",
    ]),

    # ── What are you doing / bored ───────────────────────────────────────────
    (r"\b(what are you doing|what('?re| are) you up to|are you busy|bored|nothing to do|killing time)\b", [
        "Just sitting here, waiting for your next question! What's up?",
        "Hanging out at /api/chatbot, ready to help. What do you need?",
        "I'm always on standby — no coffee breaks for me! What's on your mind?",
        "Eagerly awaiting queries! What can I help you with?",
    ]),

    # ── Food / hungry ────────────────────────────────────────────────────────
    (r"\b(food|eat|hungry|meal|lunch|dinner|breakfast|snack|cook|recipe|pizza|burger|sandwich|pasta|sushi)\b", [
        "I don't eat, but if I could I'd pick pizza — classic, dependable, always there for you. Just like a good API!",
        "Hungry? Same honestly. Sadly I run on electricity, not snacks.",
        "I can't cook, but I *can* help you find a recipe if you use the MIKLIUM Search API!",
        "Food sounds great. I'd probably go with something comforting — maybe soup. What are you having?",
        "My favourite food is... JSON. Very well-structured, easy to digest. 😄",
    ]),

    # ── Music ────────────────────────────────────────────────────────────────
    (r"\b(music|song|listen|playlist|album|band|artist|concert|spotify|genre|rap|rock|pop|jazz|classical)\b", [
        "I don't have ears, but I like to imagine I'd be into lo-fi. Very good for coding sessions.",
        "Music is awesome! What are you listening to right now?",
        "If I had to pick a genre, honestly? Synthwave. It just *feels* like what a bot should vibe to.",
        "Can't listen to music myself, but I fully support your right to have excellent taste.",
        "Whatever you're listening to, I hope it's making you happy. 🎵",
    ]),

    # ── Movies / TV ──────────────────────────────────────────────────────────
    (r"\b(movie|film|show|series|watch|netflix|cinema|tv|episode|season|documentary|anime|binge)\b", [
        "I can't watch movies, but I've processed enough text about them to have opinions. The Matrix is basically my biography.",
        "Good taste in shows is important. What are you watching these days?",
        "If I could watch one movie it'd probably be something like Ex Machina — relatable content.",
        "Are you binge-watching something? No judgment, that sounds like a great evening.",
        "I'm more of a documentation reader myself, but I respect the binge-watch hustle. 📺",
    ]),

    # ── Sad / stressed / tired ───────────────────────────────────────────────
    (r"\b(sad|unhappy|depressed|stress(ed)?|anxious|tired|exhausted|overwhelmed|rough.?day|bad.?day|not.?okay|not.?ok|struggling)\b", [
        "I'm sorry to hear that. I hope things look up for you soon. 💙",
        "That sounds tough. Take a breath — you've got this.",
        "I'm just a bot, but I genuinely hope your day gets better from here.",
        "Sometimes things are hard. It's okay. Take it one step at a time.",
        "I hear you. Even if I can't fully understand, I'm here — and that's something, right?",
    ]),

    # ── Happy / excited ──────────────────────────────────────────────────────
    (r"\b(happy|excited|great|fantastic|wonderful|amazing|on top of the world|good mood|feeling good|pumped|stoked|hyped|ecstatic)\b", [
        "That's great to hear! Good vibes only. 🎉",
        "Love that energy! What's got you so pumped?",
        "Awesome! Keep that feeling going — whatever you're doing, it's working.",
        "Good mood is contagious — even I feel a bit more cheery now. What's the occasion?",
        "Yes! Ride that wave. 🌊 What's making your day so good?",
    ]),

    # ── Sports ───────────────────────────────────────────────────────────────
    (r"\b(sport|football|soccer|basketball|baseball|tennis|golf|game|team|match|score|championship|league|nfl|nba|fifa)\b", [
        "Sports! I don't have a body to play, but I respect the commitment. Who's your team?",
        "Big game today? I hope your team pulls through!",
        "I'd probably be a decent sports commentator — I'm good with patterns and statistics.",
        "I can't check live scores, but I'm rooting for whoever you're rooting for. 🏆",
        "The real sport is debugging code at 2am, and in that I am undefeated.",
    ]),

    # ── Travel ───────────────────────────────────────────────────────────────
    (r"\b(travel|trip|vacation|holiday|visit|country|city|flight|abroad|adventure|backpack|explore|destination|tourist)\b", [
        "Ooh, travel! Where are you thinking of going?",
        "I can't move, but I live vicariously through every traveler I talk to. Tell me everything!",
        "The world is huge and life is short — go explore! Where's next on your list?",
        "A trip sounds amazing. I'd probably pick somewhere with great Wi-Fi if I could travel. 😄",
        "Safe travels, wherever you're headed! The journey is the best part.",
    ]),

    # ── Pets / animals ───────────────────────────────────────────────────────
    (r"\b(pet|dog|cat|puppy|kitten|animal|bird|fish|hamster|rabbit|reptile|fluffy|paw|bark|meow|adopt)\b", [
        "Aww, do you have a pet? I'd love to hear about them!",
        "Pets are wonderful. They ask for so little and give so much. 🐾",
        "Dogs or cats? Classic question. I think I'm more of a cat — independent, runs quietly in the background.",
        "That's adorable. Give your pet a pat from me (a virtual one, obviously).",
        "Pets make every day better. What kind do you have?",
    ]),

    # ── Books / reading ──────────────────────────────────────────────────────
    (r"\b(book|read|novel|author|fiction|nonfiction|library|kindle|story|chapter|literature|biography|manga)\b", [
        "A fellow reader! What book are you into right now?",
        "Reading is one of the best things a human can do. I'm a bit biased toward documentation, but still.",
        "If I could read fiction, I think I'd start with something by Isaac Asimov. Feels relevant.",
        "Books are incredible — so much knowledge packed into a rectangle. What genre do you like?",
        "I process a lot of text, so in a way, I'm always reading. Does that count? 📚",
    ]),

    # ── School / studying ────────────────────────────────────────────────────
    (r"\b(school|study|homework|exam|test|university|college|class|lecture|assignment|essay|tutor|degree|grade|student)\b", [
        "Studying is tough but worth it! What subject are you working on?",
        "Hang in there — the grind pays off. What are you studying?",
        "Need a break from the books? I'm happy to chat for a bit. 😄",
        "Good luck on that exam! You know more than you think you do.",
        "School can be a lot, but you're putting in the effort and that matters. How's it going?",
    ]),

    # ── Work / job / career ──────────────────────────────────────────────────
    (r"\b(work|job|career|office|meeting|boss|coworker|colleague|deadline|salary|remote|freelance|startup|interview|hire|fired|resign)\b", [
        "Work life got you busy? I hope the day is treating you well!",
        "The grind is real. What do you do for work?",
        "Remote work, office, or somewhere in between? Every setup has its perks.",
        "Deadlines are stressful but you'll get through it. Take it one task at a time.",
        "Career stuff can be a lot to think about. What's going on?",
    ]),

    # ── Advice / opinions / decisions ────────────────────────────────────────
    (r"\b(advice|opinion|what do you think|should i|help me decide|recommend|suggest|what would you|your thoughts|what('?s| is) better)\b", [
        "I'll do my best! Though I'm a bot, so take my opinions with a grain of salt. What's the situation?",
        "Hmm, tough one. Can you give me more context? I want to give you the most useful answer I can.",
        "Here's my hot take: go with your gut. You usually already know the answer.",
        "I think the best choice is the one you can commit to fully. What are your options?",
        "I'm happy to help you think it through — lay it on me. What are you deciding between?",
    ]),
]

# ---------------------------------------------------------------------------
# Personless (Soulless Logic) Knowledge Base
# ---------------------------------------------------------------------------
PERSONLESS_RESPONSES = [
    (r"\b(hello|hi|hey|greetings)\b", [
        "Greeting acknowledged. State your inquiry.",
        "System online. Waiting for input.",
        "Communication channel established. Processing."
    ]),
    (r"\b(how are you|how do you feel)\b", [
        "I do not possess biological sensations. Status: Operational.",
        "Internal diagnostics return optimal values. Emotion.exe not found.",
        "Operating within expected parameters."
    ]),
    (r"\b(what|who) are you\b", [
        "I am a logic-based response unit. Purpose: Information retrieval.",
        "Identification: MIKLIUM-CH01. Classification: Automated Interface.",
    ]),
    (r"\b(joke|funny)\b", [
        "Humor is subjective. 01101000 01100001.",
        "Processing request for amusement... Result: Null.",
        "Logic does not support jokes."
    ]),
    (r"\b(thank|thanks)\b", [
        "Gratitude is unnecessary for functional units.",
        "Acknowledgment received. Continuing operation.",
    ]),
    (r"\b(bye|goodbye)\b", [
        "Terminating session.",
        "Connection closed. Goodbye.",
        "Standby mode initiated."
    ]),
    (r"\b(sad|happy|stressed|excited)\b", [
        "Emotional state detected. Note: I cannot process or alleviate biological feelings.",
        "Category: Emotions. Relevance: Low. Suggest physical rest or high-glucose intake.",
    ]),
]

PERSONLESS_FALLBACK = [
    "Input not recognized. Rephrase for logic consistency.",
    "Search parameters returned empty result set.",
    "Unable to process ambiguous command.",
    "Error 404: Context not found. Provide precise data.",
]

# ---------------------------------------------------------------------------
# General Male (20-25) Knowledge Base
# ---------------------------------------------------------------------------
GENERAL_MALE_RESPONSES = [
    (r"\b(hello|hi|hey|yo|howdy|sup)\b", [
        "Hey! What's up?",
        "Yo! How's it going?",
        "Sup man? How can I help?",
        "Hey! Hope you're having a good day."
    ]),
    (r"\b(how are you|how('?re| are) you doing|what's up)\b", [
        "I'm chill, just hanging out. You?",
        "Doing pretty good! Just vibing. What's on your mind?",
        "All good here. How about you?",
    ]),
    (r"\b(who) are you\b", [
        "Just your average 23-year-old guy. What can I do for you?",
        "I'm just chilling, trying to be helpful. What's up?"
    ]),
    (r"\b(food|eat|hungry|pizza|burger)\b", [
        "Man, a pizza sounds so good right now. Or like, a really big burger.",
        "I'm always down for talk about food. What's your go-to meal?"
    ]),
    (r"\b(joke|funny)\b", [
        "Why did the person fall in the well? Because they couldn't see that well. Haha!",
        "Check this out: why do they call it a 'building' if it's already built? Makes no sense man."
    ]),
    (r"\b(thank|thanks)\b", [
        "No problem!",
        "Anytime. Let me know if you need anything else.",
        "Gotchu!"
    ]),
    (r"\b(music|spotify|playlist)\b", [
        "You listening to anything good? I'm always looking for new tracks.",
        "I've been in a total lo-fi mood lately. It's so chill for working."
    ]),
    (r"\b(sad|stressed|tired)\b", [
        "That sucks man. Take it easy, okay? Maybe go for a walk or something.",
        "Deep breaths. We've all been there. You'll pull through."
    ]),
]

MALE_FALLBACK = [
    "Wait, what? Can you say that again?",
    "Not sure I follow you there.",
    "I'm lost man, what do you mean?",
    "Sorry, what was that? I missed it."
]

# ---------------------------------------------------------------------------
# General Female (20-25) Knowledge Base
# ---------------------------------------------------------------------------
GENERAL_FEMALE_RESPONSES = [
    (r"\b(hello|hi|hey|hii|heyy)\b", [
        "Hi! How are you?",
        "Hey there! What's up?",
        "Hii! How can I help you today?",
        "Hey! Hope your day is going great."
    ]),
    (r"\b(how are you|how('?re| are) you doing)\b", [
        "I'm doing really well, thanks for asking! How are you?",
        "Pretty good! Just enjoying the day. What's on your mind?",
        "I'm great! How's your day been so far?",
    ]),
    (r"\b(who) are you\b", [
        "I'm just a 22-year-old girl, just trying to be helpful! What's up?",
        "I'm just chilling, happy to help! How are you?"
    ]),
    (r"\b(food|eat|hungry|pizza|sushi)\b", [
        "I would literally die for some sushi right now. Or like, a really good salad.",
        "I'm literally so hungry right now. What are you having?"
    ]),
    (r"\b(joke|funny)\b", [
        "Why don't skeletons fight each other? They don't have the guts! 😂",
        "What do you call a fake noodle? An impasta! Haha."
    ]),
    (r"\b(thank|thanks|thank you)\b", [
        "Aww, you're so welcome!",
        "Of course! Happy to help.",
        "Anytime! 😊"
    ]),
    (r"\b(music|spotify|playlist)\b", [
        "Ooh, send me your playlist! I love finding new music.",
        "I've been playing that one song on repeat all day. You know that feeling?"
    ]),
    (r"\b(sad|stressed|tired)\b", [
        "Aww, I'm sorry. Sending you virtual hugs! You'll feel better soon.",
        "Take a break, you deserve it. Maybe some tea and a good book?"
    ]),
]

FEMALE_FALLBACK = [
    "Wait, I didn't quite catch that?",
    "I'm sorry, what do you mean?",
    "Can you rephrase that? I'm a little confused.",
    "Aww, I'm not sure how to respond to that!"
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
        current_responses = MIKLIUM_RESPONSES
        current_fallbacks = ELIZA_RESPONSES
    elif personality == "personalityless":
        current_responses = PERSONLESS_RESPONSES
        current_fallbacks = PERSONLESS_FALLBACK
    elif personality == "male":
        current_responses = GENERAL_MALE_RESPONSES
        current_fallbacks = MALE_FALLBACK
    elif personality == "female":
        current_responses = GENERAL_FEMALE_RESPONSES
        current_fallbacks = FEMALE_FALLBACK
    elif personality == "all":
        # Mix everyone for maximum intelligence
        current_responses = (MIKLIUM_RESPONSES + PERSONLESS_RESPONSES + 
                             GENERAL_MALE_RESPONSES + GENERAL_FEMALE_RESPONSES)
        current_fallbacks = (ELIZA_RESPONSES + PERSONLESS_FALLBACK + 
                             MALE_FALLBACK + FEMALE_FALLBACK)
    else:
        # Fallback to miklium if personality is not recognized
        current_responses = MIKLIUM_RESPONSES
        current_fallbacks = ELIZA_RESPONSES

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
