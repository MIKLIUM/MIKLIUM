import re

RESPONSES = [
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

FALLBACK = [
    "Input not recognized. Rephrase for logic consistency.",
    "Search parameters returned empty result set.",
    "Unable to process ambiguous command.",
    "Error 404: Context not found. Provide precise data.",
]
