from fastapi import FastAPI, Request
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from gsheet import GoogleSheetsHandler
import os
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())
gsheet_handler = GoogleSheetsHandler()

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET")

# Verify credentials are loaded
if not SLACK_BOT_TOKEN or not SLACK_SIGNING_SECRET:
    raise ValueError("Missing required Slack credentials in environment variables")

print(f"Bot Token starts with: {SLACK_BOT_TOKEN[:10]}...")
print(f"Signing Secret starts with: {SLACK_SIGNING_SECRET[:10]}...")

# Initialize Bolt app
bolt_app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET
)

# Listen to messages in channels
@bolt_app.event("message")
def handle_message(event, say, client):
    """Handle all channel messages"""
    try:
        # Get message details
        text = event.get("text", "")
        user_id = event.get("user")
        channel_id = event.get("channel")
        timestamp = event.get("ts")
        
        channel_info = client.conversations_info(channel=channel_id)
        channel_name = channel_info["channel"]["name"]
        
        MONITORED_CHANNELS = ["timestamp", "workhours"]
        
        if channel_name in MONITORED_CHANNELS:
            user_info = client.users_info(user=user_id)
            username = user_info["user"]["real_name"]
            
            from datetime import datetime
            dt = datetime.fromtimestamp(float(timestamp))
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            
            # Print to terminal
            print(f"\n{'='*60}")
            print(f"Channel: #{channel_name}")
            print(f"User: {username} (@{user_info['user']['name']}) | User Id: {user_id}")
            print(f"Message: {text}")
            print(f"Timestamp: {formatted_time}")
            print(f"{'='*60}\n")
            
            print(f"==Sending DATA to Google Sheet Process==\n")
            gsheet_handler.send_to_google_sheets(
                channel=channel_name,
                username=username,
                message=text,
                timestamp=formatted_time
            )
            
    except Exception as e:
        print(f"Error processing message: {e}")

# Create handler
handler = SlackRequestHandler(bolt_app)

# Initialize FastAPI
app = FastAPI()

@app.post("/slack/events")
async def slack_events(req: Request):
    """Handle Slack events"""
    try:
        return await handler.handle(req)
    except Exception as e:
        print(f"Error handling request: {e}")
        return {"error": str(e)}

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "Slack bot is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)