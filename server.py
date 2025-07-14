# main.py

import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GHL_CLIENT_ID = os.getenv("GHL_CLIENT_ID")
GHL_CLIENT_SECRET = os.getenv("GHL_CLIENT_SECRET")
GHL_REDIRECT_URI = os.getenv("GHL_REDIRECT_URI")

app = FastAPI()

@app.get("/")
async def root():
    auth_url = (
        "https://marketplace.gohighlevel.com/oauth/chooselocation"
        f"?response_type=code"
        f"&redirect_uri={GHL_REDIRECT_URI}"
        f"&client_id={GHL_CLIENT_ID}"
        "&scope=contacts.readonly+contacts.write+conversations.readonly+conversations.write+"
        "conversations/message.readonly+conversations/message.write+locations.readonly+"
        "opportunities.readonly+opportunities.write+calendars.readonly+calendars.write+"
        "calendars/events.readonly+calendars/events.write+forms.readonly+forms.write"
        "&state=secure123"
    )
    return HTMLResponse(f"""
        <h2>🚀 GoHighLevel OAuth Token Generator</h2>
        <p><a href="{auth_url}">Click here to authorize and get your token</a></p>
    """)


@app.get("/oauth/callback")
async def oauth_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return {"error": "Missing code in callback."}

    token_url = "https://services.leadconnectorhq.com/oauth/token"

    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": GHL_CLIENT_ID,
            "client_secret": GHL_CLIENT_SECRET,
            "redirect_uri": GHL_REDIRECT_URI,
        })

    if response.status_code != 200:
        print("❌ Token exchange failed:", response.text)
        return {"error": "Token exchange failed", "details": response.text}

    token_data = response.json()

    # ✅ Log token to Railway logs
    print("\n🔐 GHL Access Token Received:")
    print(json.dumps(token_data, indent=2))

    # ✅ Save to file
    with open(".token.json", "w") as f:
        json.dump(token_data, f, indent=2)

    return HTMLResponse("""
    <h2>✅ Token stored successfully!</h2>
    <p>Check Railway logs to copy your token from the backend.</p>
    """)

