"""
This script tests all MIKLIUM APIs.
It should be run after EVERY change to confirm nothing is broken.
"""

import requests
import json

BASE_URL = "https://miklium.vercel.app"

TESTS = [
    {
        "name": "Python Sandbox API",
        "endpoint": "/api/python-sandbox",
        "payload": {"code": "print('MIKLIUM TEST SUCCESS')"},
        "expected_key": "success",
        "expected_val": True
    },
    {
        "name": "Search API",
        "endpoint": "/api/search",
        "payload": {"search": ["miklium"]},
        "expected_key": "success",
        "expected_val": True
    },
    {
        "name": "Shortcut Info API",
        "endpoint": "/api/shortcut-info",
        "payload": {"url": "https://routinehub.co/shortcut/18431/"},
        "expected_key": "success",
        "expected_val": True
    },
    {
        "name": "YouTube Transcript API",
        "endpoint": "/api/youtube-transcript",
        "payload": {"url": "https://youtu.be/Qz8u00pX738"},
        "expected_key": "success",
        "expected_val": True
    },
    {
        "name": "Chatbot API",
        "endpoint": "/api/chatbot",
        "payload": {"message": "Hello"},
        "expected_key": "response"
    }
]

def run_tests():
    print(f"Starting MIKLIUM API Tests on {BASE_URL}...\n")
    passed = 0
    total = len(TESTS)

    for test in TESTS:
        url = BASE_URL + test["endpoint"]
        try:
            response = requests.post(url, json=test["payload"], timeout=15)
            data = response.json()
            
            # Simple check logic
            status = False
            if "expected_val" in test:
                status = data.get(test["expected_key"]) == test["expected_val"]
            else:
                status = test["expected_key"] in data

            if status:
                print(f"✅ {test['name']}: Passed")
            else:
                print(f"❌ {test['name']}: Failed (Status: {response.status_code})")
            
            print(f"   Response: {json.dumps(data, indent=2)}\n")
            if status: passed += 1
            
        except Exception as e:
            print(f"❌ {test['name']}: Error occurred: {e}\n")

    print(f"\nSummary: {passed}/{total} tests passed.")

if __name__ == "__main__":
    run_tests()
