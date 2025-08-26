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
settings_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.dirname(settings_dir))
candidates_token = os.path.join(project_root, 'utls/token.json')
credentials_files = os.path.join(project_root, 'utls/credentials.json')


def consumer_so_data(unit_id):
    """
    get the data from the new employee google sheet
    """
    CONS_RANGE_NAME="Cons_SO_ID!A1:R"
    PCL_RANGE_NAME="PCL_SO_ID!A1:R"
    CONS_SPREADSHEET_ID = "1OKDekAdz6RkzINmYgIiDzRFDHw06ef9Aj67OShLI0NI"
    TK_Food_SPREADSHEET_ID = "1ZVKcTBFGDw4lRKlvXrErcVWnn_QAaVXPBdaxg94-o3k"
    TK_Food_RANGE_NAME="SO_ID!A1:R"
    
    unit_id = int(unit_id)
    if unit_id == 1:
        RANGE_NAME = CONS_RANGE_NAME
        SPREADSHEET_ID = CONS_SPREADSHEET_ID
    elif unit_id == 3:
        RANGE_NAME = PCL_RANGE_NAME
        SPREADSHEET_ID = CONS_SPREADSHEET_ID
    elif unit_id == 2:
        RANGE_NAME = TK_Food_RANGE_NAME
        SPREADSHEET_ID = TK_Food_SPREADSHEET_ID

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
                SO_ID = row[0]
                key = SO_ID
                entry = {headers[i]: (row[i] if i < len(row) else None) for i in range(len(headers))}
                data_dict[key] = entry

            json_data = json.dumps(data_dict, indent=4)
            return json.loads(json_data)
    
    except HttpError as err:
        print(err)
        return {}


