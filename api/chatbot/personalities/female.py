import re

RESPONSES = [
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

FALLBACK = [
    "Wait, I didn't quite catch that?",
    "I'm sorry, what do you mean?",
    "Can you rephrase that? I'm a little confused.",
    "Aww, I'm not sure how to respond to that!"
]
