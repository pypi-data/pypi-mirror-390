#!/usr/bin/env python3
"""Simple CLI chat client that maintains session."""

import requests
import json
import sys

API_URL = "http://localhost:8000/api/chat"
session_id = None
user_id = input("Enter your user ID (or press Enter for 'sam'): ").strip() or "sam"

print(f"\n🤖 Chatbot ready! Type your messages (or 'quit' to exit)\n")

while True:
    user_message = input(f"You: ").strip()

    if not user_message:
        continue

    if user_message.lower() in ['quit', 'exit', 'q']:
        print("👋 Goodbye!")
        break

    # Build request
    payload = {
        "user_id": user_id,
        "message": user_message
    }

    # Include session_id if we have one
    if session_id:
        payload["session_id"] = session_id

    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()

        data = response.json()

        # Save session_id for next message
        if not session_id:
            session_id = data.get("session_id")
            print(f"📝 Session started: {session_id}\n")

        # Display assistant response
        print(f"Assistant: {data.get('message', 'No response')}\n")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}\n")
    except json.JSONDecodeError:
        print(f"❌ Invalid response from server\n")
