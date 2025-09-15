import os.path
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import phonenumbers
from googleapiclient.http import MediaIoBaseDownload
import io
from django.core.files.base import ContentFile

# Google Sheet and Google drive authentication class
# <__________________________________________________>
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

class BaseGoogleSheetAuthentication:
    drive_scopes = ["https://www.googleapis.com/auth/drive"]
    sheet_scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    settings_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.dirname(settings_dir))
    drive_token = os.path.join(project_root, "utils/drive_token.json")
    sheet_token = os.path.join(project_root, "utils/sheet_token.json")
    credentials_files = os.path.join(project_root, "utils/credentials.json")

    def __init__(self):
        self.drive_creds = None
        self.sheet_creds = None
        self.SPREADSHEET_ID = None
        self.RANGE_NAME = "Form Responses 1!A1:AG"

        if os.path.exists(self.sheet_token):
            self.sheet_creds = Credentials.from_authorized_user_file(
                self.sheet_token, self.sheet_scopes
            )

        if not self.sheet_creds or not self.sheet_creds.valid:
            if (
                self.sheet_creds
                and self.sheet_creds.expired
                and self.sheet_creds.refresh_token
            ):
                self.sheet_creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_files, self.sheet_scopes
                )
                self.sheet_creds = flow.run_local_server(port=0)
            with open(self.sheet_token, "w") as sheet_token:
                sheet_token.write(self.sheet_creds.to_json())

        if os.path.exists(self.drive_token):
            self.drive_creds = Credentials.from_authorized_user_file(
                self.drive_token, self.drive_scopes
            )

        if not self.drive_creds or not self.drive_creds.valid:
            if (
                self.drive_creds
                and self.drive_creds.expired
                and self.drive_creds.refresh_token
            ):
                self.drive_creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_files, self.drive_scopes
                )
                self.drive_creds = flow.run_local_server(port=0)
            with open(self.drive_token, "w") as drive_token:
                drive_token.write(self.drive_creds.to_json())


class CandidateGoogleSheet(BaseGoogleSheetAuthentication):
    def __init__(self):
        super().__init__()

    def get_candidate_data_google_sheet(self, spreadsheet_id, last_row):
        self.SPREADSHEET_ID = spreadsheet_id
        self.Last_row = last_row
        try:
            service = build("sheets", "v4", credentials=self.sheet_creds)

            # Call the Sheets API
            sheet = service.spreadsheets()
            result = (
                sheet.values()
                .get(spreadsheetId=self.SPREADSHEET_ID, range=self.RANGE_NAME)
                .execute()
            )
            
            values = result.get("values", [])
            if not values:
                print("No data found.")
                return {}
            else:
                headers = values[0]
                rows = values[self.Last_row:]
                data_list = []
                for row in rows:
                    file_id = row[9].split("=", 1)[1]
                    data = {
                        headers[i]: (row[i] if i < len(row) else None)
                        for i in range(len(headers))
                    }

                    data.update({"file_id": file_id})
                    data_list.append(data)
                return data_list

        except HttpError as err:
            print(err)
            return {}

    def download_resume(self, file_id):
        try:
            service = build("drive", "V3", credentials=self.drive_creds)
            file_metadata = service.files().get(fileId=file_id, fields="name, mimeType").execute()
            filename = file_metadata.get("name")  # original name with extension
            request = service.files().get_media(fileId=file_id)
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print(f"downlod {int(status.progress()*100)}.")
            file.seek(0)
            return ContentFile(file.read(), name=filename)
        except HttpError as err:
            print(err)
            return {}

    @property
    def candidate_details_data(self):
        """
        get the data from the new employee google sheet
        """
        self.SPREADSHEET_ID = "18w9lwZrOWUOjU2jaKtX46DoJ3Y7IrHZjLhay2s4RriY" 
        try:
            service = build("sheets", "v4", credentials=self.sheet_creds)

            # Call the Sheets API
            sheet = service.spreadsheets()
            result = (
                sheet.values().get(spreadsheetId=self.SPREADSHEET_ID, range=self.RANGE_NAME).execute()
            )
            values = result.get("values", [])
            if not values:
                print("No data found.")
                return {}
            else:
                headers = values[0]
                rows = values[1:]

                data_dict = {}
                for row in rows:
                    mobile_no = phonenumbers.parse(row[2], "BD")
                    mobile_no = phonenumbers.format_number(
                        mobile_no, phonenumbers.PhoneNumberFormat.E164
                    )
                    key = mobile_no
                    entry = {
                        headers[i]: (row[i] if i < len(row) else None)
                        for i in range(len(headers))
                    }
                    data_dict[key] = entry

                json_data = json.dumps(data_dict, indent=4)
                return json.loads(json_data)

        except HttpError as err:
            print(err)
            return {}

