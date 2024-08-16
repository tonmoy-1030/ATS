import os.path
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import phonenumbers

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = "1GuHAL5BjOPgH3P1KbBXaQifmFbyCcEi7m548XSaGXUw"
RANGE_NAME = "Form Responses 1!A1:AG"
settings_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.dirname(settings_dir))
candidates_token = os.path.join(project_root, 'utls/token.json')
credentials_files = os.path.join(project_root, 'utls/credentials.json')


def NewEmployeeData():
    """
    get the data from the new employee google sheet
    """
    creds = None
    if os.path.exists(candidates_token):
        creds = Credentials.from_authorized_user_file(candidates_token, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_files, SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(candidates_token, "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME)
            .execute()
        )
        values = result.get("values", [])
        if not values:
            print('No data found.')
            return {}
        else:
            headers = values[0]
            rows = values[1:]
      
            data_dict = {}
            for row in rows:
                mobile_no = phonenumbers.parse(row[2], 'BD')
                mobile_no = phonenumbers.format_number(mobile_no, phonenumbers.PhoneNumberFormat.E164)
                key = mobile_no
                entry = {headers[i]: (row[i] if i < len(row) else None) for i in range(len(headers))}
                data_dict[key] = entry

            json_data = json.dumps(data_dict, indent=4)
            return json.loads(json_data)

    except HttpError as err:
        print(err)
        return {}
