import os
import random
import httpx
from fastapi import FastAPI, Header, HTTPException

app = FastAPI()

NTFY_TOPIC = os.getenv("NTFY_TOPIC")  # Something secret like "our-love-sync-882"
API_KEY = os.getenv("API_KEY")
NTFY_URL = os.getenv("NTFY_URL")

MESSAGES = [
    ("Just thought of you!", "❤️"),
    ("Quick brain-sync initiated.", "🧠"),
    ("Miss you already.", "🥺"),
    ("Error: Brain overloaded with thoughts of you.", "🔥"),
    ("HOOOOOLIIIIISSSSS", "❤️"),
    ("Te amo.<", "❤️"),
    ("Hola, mi amorcita. Just been thinking of you.", "❤️"),
    ("My hear... It burns... With LOVE FOR YOU", "❤️"),
    ("I love you", "❤️"),
    ("Te Amo!", "❤️"),
]


@app.post("/thought")
async def send_ntfy_thought(x_api_key: str | None = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403)

    text, emoji = random.choice(MESSAGES)

    async with httpx.AsyncClient() as client:
        # We send headers to ntfy to control the notification's look
        await client.post(
            f"{NTFY_URL}/{NTFY_TOPIC}",
            data=text,
            headers={
                "Title": "Smart ❤️",
                "Priority": "high",  # Makes it pop up immediately
                "Tags": emoji,  # Adds an emoji to the notification icon
                # "Click": "https://yourdomain.com",  # Optional: click to open a site
            },
        )
    return {"status": "sent"}
