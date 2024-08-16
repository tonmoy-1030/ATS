from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import phonenumbers
import os.path


settings_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.dirname(settings_dir))
candidates_token = os.path.join(project_root, 'utls/candidates_token.json')
credentials_files = os.path.join(project_root, 'utls/credentials.json')

SCOPES = ["https://www.googleapis.com/auth/forms.responses.readonly"]

def get_authenticated_service():
    creds = None
    if os.path.exists(candidates_token):
        creds = Credentials.from_authorized_user_file(candidates_token, SCOPES)
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
    return build("forms", "v1", credentials=creds)

def get_form_responses(service, form_id):
    """
    Retrieves responses for a specified Google Form ID.
    """
    try:
        results = service.forms().responses().list(formId=form_id).execute()
        return results.get('responses', [])
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def process_responses(responses):
    """
    Processes retrieved responses, extracts phone numbers, and stores them in a dictionary.
    """

    response_list = []
    for response in responses:
        mobile_no = None
        response_values = {}
        for key, value in response.items():
            if key == 'answers':
                for question_id, answer_data in value.items():
                    if 'textAnswers' in answer_data:
                        answer = answer_data['textAnswers']['answers'][0]['value']
                        if question_id == '09dbb7cd':
                            mobile_no = answer
                    elif 'fileUploadAnswers' in answer_data:
                        answer = answer_data['fileUploadAnswers']['answers'][0]['fileName']
                    response_values[question_id] = answer
        if mobile_no:
            try:
                mobile_no = phonenumbers.parse(mobile_no, 'BD')
                mobile_no = phonenumbers.format_number(mobile_no, phonenumbers.PhoneNumberFormat.E164)
            except phonenumbers.NumberParseException as e:
                print(f"Error parsing phone number: {e}")
                mobile_no = None
        if mobile_no:
            response_list.append({mobile_no: response_values})
    return response_list

# form_id = "1p1PLHd3_ywCkAYKVT9_b0pP4Mp1GWnTmKnCqZEV8Rwc"

# service = get_authenticated_service()
# responses = get_form_responses(service, form_id)
# if responses:
#     processed_responses = process_responses(responses)
#     print(processed_responses)
# else:
#     print("No responses found for the specified form.")

