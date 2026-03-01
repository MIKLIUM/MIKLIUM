import re

RESPONSES = [
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

FALLBACK = [
    "Wait, what? Can you say that again?",
    "Not sure I follow you there.",
    "I'm lost man, what do you mean?",
    "Sorry, what was that? I missed it."
]
