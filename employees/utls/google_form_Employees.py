import os.path
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import phonenumbers
from decouple import config



class BaseGoogleSheetAuthentication():
    """
    Base class for Google Sheet Authentication
    """
    
    # If modifying these scopes, delete the file token.json.
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# The ID and range of a sample spreadsheet.
    SPREADSHEET_ID = config("EMPLOYEE_SPREADSHEET_ID")
    RANGE_NAME = "Form Responses 1!A1:AG"
    settings_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.dirname(settings_dir))
    candidates_token = os.path.join(project_root, 'utls/token.json')
    credentials_files = os.path.join(project_root, 'utls/credentials.json')

    def __init__(self):
        self.creds = None
        if os.path.exists(self.candidates_token):
            self.creds = Credentials.from_authorized_user_file(self.candidates_token, self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_files, self.SCOPES
                )
                self.creds = flow.run_local_server(port=0)
            with open(self.candidates_token, "w") as token:
                token.write(self.creds.to_json())


class NewEmployeeData(BaseGoogleSheetAuthentication):
    """
    get the data from the new employee google sheet
    """

    def __init__(self):
        super().__init__()

    def get_employee_data(self):
        try:
            service = build("sheets", "v4", credentials=self.creds)

            # Call the Sheets API
            sheet = service.spreadsheets()
            result = (
                sheet.values()
                .get(spreadsheetId=self.SPREADSHEET_ID, range=self.RANGE_NAME)
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
        
    def consumer_so_data(self, unit_id):
        """
        get the data from the new employee google sheet
        """
        CONS_RANGE_NAME="Cons_SO_ID!A1:R"
        PCL_RANGE_NAME="PCL_SO_ID!A1:R"
        TK_Food_RANGE_NAME="SO_ID!A1:R"
        CONS_SPREADSHEET_ID = config("CONS_SPREADSHEET_ID")
        TK_Food_SPREADSHEET_ID = config("TK_Food_SPREADSHEET_ID")
        
        unit_id = int(unit_id)
        if unit_id == 1:
            self.RANGE_NAME = CONS_RANGE_NAME
            self.SPREADSHEET_ID = CONS_SPREADSHEET_ID
        elif unit_id == 3:
            self.RANGE_NAME = PCL_RANGE_NAME
            self.SPREADSHEET_ID = CONS_SPREADSHEET_ID
        elif unit_id == 2:
            self.RANGE_NAME = TK_Food_RANGE_NAME
            self.SPREADSHEET_ID = TK_Food_SPREADSHEET_ID

        try:
            service = build("sheets", "v4", credentials=self.creds)

            # Call the Sheets API
            sheet = service.spreadsheets()
            result = (
                sheet.values()
                .get(spreadsheetId=self.SPREADSHEET_ID, range=self.RANGE_NAME)
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
