import os
import random
import secrets
import httpx
from typing import Annotated
from pydantic import BaseModel
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse

app = FastAPI()
security = HTTPBasic()

NTFY_TOPIC = os.getenv("NTFY_TOPIC")
API_KEY = os.getenv("API_KEY")
NTFY_URL = os.getenv("NTFY_URL")


class ThoughtPayload(BaseModel):
    message: str | None = None


def verify_credentials(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    if API_KEY:
        correct_password_bytes = API_KEY.encode("utf8")
        current_password_bytes = credentials.password.encode("utf8")
        is_correct_password = secrets.compare_digest(
            current_password_bytes, correct_password_bytes
        )
        if not is_correct_password:
            raise HTTPException(
                status_code=401,
                detail="Incorrect credentials",
                headers={"WWW-Authenticate": "Basic"},
            )
    return credentials.username


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


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Heart</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0f172a;
            --container-bg: rgba(30, 41, 59, 0.7);
            --border-color: rgba(255, 255, 255, 0.1);
            --text-color: #f8fafc;
            --accent-color: #ef4444;
            --accent-hover: #dc2626;
        }
        body {
            margin: 0;
            padding: 0;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background: linear-gradient(135deg, var(--bg-color), #000000);
            font-family: 'Outfit', sans-serif;
            color: var(--text-color);
        }
        .container {
            background: var(--container-bg);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--border-color);
            border-radius: 24px;
            padding: 40px;
            width: 100%;
            max-width: 400px;
            box-sizing: border-box;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            transform: translateY(0);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .container:hover {
            transform: translateY(-5px);
            box-shadow: 0 30px 60px -12px rgba(239, 68, 68, 0.2);
        }
        h1 {
            margin: 0 0 24px 0;
            font-weight: 600;
            font-size: 24px;
            text-align: center;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        .heart-icon {
            color: var(--accent-color);
            animation: pulse 2s infinite;
            display: inline-block;
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.15); }
            100% { transform: scale(1); }
        }
        textarea {
            width: 100%;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 16px;
            color: var(--text-color);
            font-family: inherit;
            font-size: 16px;
            resize: vertical;
            min-height: 100px;
            box-sizing: border-box;
            outline: none;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
        }
        textarea:focus {
            border-color: var(--accent-color);
            box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.2);
        }
        button {
            width: 100%;
            background: var(--accent-color);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 16px;
            font-size: 16px;
            font-weight: 600;
            font-family: inherit;
            margin-top: 20px;
            cursor: pointer;
            transition: background 0.3s ease, transform 0.1s ease;
        }
        button:hover {
            background: var(--accent-hover);
        }
        button:active {
            transform: scale(0.98);
        }
        .status {
            margin-top: 16px;
            text-align: center;
            font-size: 14px;
            min-height: 20px;
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        .status.show {
            opacity: 1;
        }
        .status.success { color: #4ade80; }
        .status.error { color: #f87171; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Send a Thought <span class="heart-icon">❤️</span></h1>
        <form id="thoughtForm">
            <textarea id="thoughtText" placeholder="What's on your mind? (Leave empty for a random sweet message)"></textarea>
            <button type="submit">Dispatch Thought</button>
        </form>
        <div id="statusMsg" class="status"></div>
    </div>
    <script>
        document.getElementById('thoughtForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = e.target.querySelector('button');
            const statusMsg = document.getElementById('statusMsg');
            const text = document.getElementById('thoughtText').value;
            
            btn.disabled = true;
            btn.textContent = 'Sending...';
            statusMsg.className = 'status';
            
            try {
                const response = await fetch('/dispatch', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: text || null })
                });
                
                if (response.ok) {
                    statusMsg.textContent = 'Thought sent successfully! ✨';
                    statusMsg.classList.add('show', 'success');
                    document.getElementById('thoughtText').value = '';
                } else {
                    const data = await response.json();
                    statusMsg.textContent = data.detail || 'Failed to send thought.';
                    statusMsg.classList.add('show', 'error');
                }
            } catch (err) {
                statusMsg.textContent = 'Network error occurred.';
                statusMsg.classList.add('show', 'error');
            } finally {
                btn.disabled = false;
                btn.textContent = 'Dispatch Thought';
                setTimeout(() => {
                    statusMsg.classList.remove('show');
                }, 3000);
            }
        });
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def get_interface(username: str = Depends(verify_credentials)):
    return HTML_TEMPLATE


@app.post("/dispatch")
async def dispatch_thought(
    payload: ThoughtPayload, username: str = Depends(verify_credentials)
):
    if not NTFY_TOPIC:
        raise HTTPException(status_code=500, detail="NTFY_TOPIC not configured")

    if payload.message:
        text, emoji = payload.message, "❤️"
    else:
        text, emoji = random.choice(MESSAGES)

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{NTFY_URL}/{NTFY_TOPIC}",
                data=text,
                headers={
                    "Title": "Smart Heart",
                    "Priority": "high",
                    "Tags": "heart",
                },
            )
            resp.raise_for_status()
        except httpx.HTTPError as e:
            print(f"Error sending ntfy: {e}")
            raise HTTPException(status_code=502, detail="Failed to send notification")

    return {"status": "sent"}


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
        # We send JSON to ntfy to support emojis (headers only support ASCII/Latin-1)
        try:
            resp = await client.post(
                f"{NTFY_URL}/{NTFY_TOPIC}",
                data=text,
                headers={
                    "Title": "Smart Heart",
                    "Priority": "high",  # Makes it pop up immediately
                    "Tags": "heart",  # Adds an emoji to the notification icon
                    # "Click": "https://yourdomain.com",  # Optional: click to open a site
                },
            )
            resp.raise_for_status()
        except httpx.HTTPError as e:
            print(f"Error sending ntfy: {e}")
            raise HTTPException(status_code=502, detail="Failed to send notification")

    return {"status": "sent"}
