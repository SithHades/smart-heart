import os
import random
import httpx
from fastapi import FastAPI, Header, HTTPException

app = FastAPI()

NTFY_TOPIC = os.getenv("NTFY_TOPIC")
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


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/thought")
async def send_ntfy_thought(x_api_key: str | None = Header(None)):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=403)

    if not NTFY_TOPIC:
        raise HTTPException(status_code=500, detail="NTFY_TOPIC not configured")

    text, emoji = random.choice(MESSAGES)

    async with httpx.AsyncClient() as client:
        # We send headers to ntfy to control the notification's look
        try:
            resp = await client.post(
                f"{NTFY_URL}/{NTFY_TOPIC}",
                data=text,
                headers={
                    "Title": "Smart ❤️",
                    "Priority": "high",  # Makes it pop up immediately
                    "Tags": emoji,  # Adds an emoji to the notification icon
                    # "Click": "https://yourdomain.com",  # Optional: click to open a site
                },
            )
            resp.raise_for_status()
        except httpx.HTTPError as e:
            print(f"Error sending ntfy: {e}")
            raise HTTPException(status_code=502, detail="Failed to send notification")

    return {"status": "sent"}
