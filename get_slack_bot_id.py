import os
from dotenv import find_dotenv, load_dotenv

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt import App

# Load .env
load_dotenv(find_dotenv())

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]

app = App(token=SLACK_BOT_TOKEN)

def get_bot_user_id():
    try:
        slack_client = WebClient(token=SLACK_BOT_TOKEN)
        response = slack_client.auth_test()
        print(f"RESPONSE: {response}")  # This will show the full response
        return response["user_id"]

    except SlackApiError as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    bot_user_id = get_bot_user_id()
    print("Bot User ID:", bot_user_id)