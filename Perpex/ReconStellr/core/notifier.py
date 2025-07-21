# core/notifier.py (Optional if you want notifications)
import os
import requests

def post_to_slack(message):
    SLACK_URL = os.getenv("SLACK_WEBHOOK")
    if not SLACK_URL:
        return
    requests.post(SLACK_URL, json={"text": message})
