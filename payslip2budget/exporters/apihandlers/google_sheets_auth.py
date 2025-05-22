import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these SCOPES, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Placeholder for the path to the credentials.json file
# This will likely be passed in or configured elsewhere
CREDENTIALS_FILE = 'credentials.json' 
TOKEN_FILE = 'token.json'

def get_sheets_service(credentials_path: str = CREDENTIALS_FILE):
    """Shows basic usage of the Sheets API.
    Prints the names and ids of the first 10 spreadsheets the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(
                    f"Credentials file not found at {credentials_path}. "
                    f"Please download it from Google Cloud Console and place it as {credentials_path}."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)
        return service
    except HttpError as err:
        print(err)
        # Consider how to handle errors, maybe raise them
        return None

if __name__ == "__main__":
    # Example usage:
    # 1. Make sure you have credentials.json in the same directory or provide path
    # 2. Run this script. It will open a browser for authentication on the first run.
    # 3. It will then list some spreadsheets if successful.
    service = get_sheets_service()
    if service:
        try:
            # Call the Sheets API (Example: list spreadsheets)
            result = service.spreadsheets().get(spreadsheetId="").execute() # Dummy call, will fail without valid ID
            # Actually, a better test for a new setup is to list some files from Drive that are sheets
            # or just rely on the build() not failing.
            # For now, just confirm service object creation.
            print("Successfully obtained Google Sheets API service object.")
            # Example: Get spreadsheet metadata (replace with a valid spreadsheetId)
            # spreadsheet_id = 'YOUR_SPREADSHEET_ID' 
            # result = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            # print(f"The title of the spreadsheet is: {result.get('properties').get('title')}")
        except HttpError as error:
            print(f"An API error occurred: {error}")
            print("Ensure you have a valid spreadsheetId for testing or that credentials.json has Sheets API enabled.")
