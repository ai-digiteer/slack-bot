import gspread
from google.oauth2.service_account import Credentials
import os

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "credentials.json")
SPREADSHEET_ID = os.getenv("GOOGLE_SHEET_ID", "1lRDZ5fCrmLWB-At5iLSOJiN217tRb5n8qI9zoO8_rKY")
DEFAULT_HEADERS = ["Channel", "User Name", "Message", "Timestamp"]


class GoogleSheetsHandler:
    def __init__(self):
        self.client = self._get_client()
        self.spreadsheet = self.client.open_by_key(SPREADSHEET_ID)

    def _get_client(self):
        creds = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=SCOPES
        )
        return gspread.authorize(creds)
    

    def _get_worksheet(self, sheet_name: str):
        """Get worksheet by name, or create it if it doesn't exist."""
        if not sheet_name:
            raise ValueError("Worksheet name must be provided.")

        try:
            worksheet = self.spreadsheet.worksheet(sheet_name)
            print(f"✅ Found worksheet '{sheet_name}'")
        except gspread.WorksheetNotFound:
            print(f"Worksheet '{sheet_name}' not found. Creating a new one...")
            worksheet = self.spreadsheet.add_worksheet(title=sheet_name, rows="1000", cols="1000")
            worksheet.append_row(DEFAULT_HEADERS)
            worksheet.format("A1:D1", {"textFormat": {"bold": True}})
            print(f"Worksheet '{sheet_name}' created with bold headers.")

        return worksheet
    

    def send_to_google_sheets(self, channel: str, username: str, message: str, timestamp: str):
        """Appends a row to the sheet corresponding to the channel name."""
        try:
            worksheet = self._get_worksheet(channel)
            row = [channel, username, message, timestamp]
            worksheet.append_row(row)
            print(f"✅ Data appended successfully to '{channel}': {row}")
        except Exception as e:
            print(f"❌ Error appending to Google Sheet: {e}")