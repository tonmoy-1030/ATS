import requests
import json
from decouple import config


def send_single_sms(msisdn=[], message=""):
    try:
        headers = {"Content-Type": "application/json"}
        payload = {
            "username": config("GP_USERNAME"),
            "password": config("GP_PASSWORD"),
            "apicode": config("APICODE"),
            "msisdn": msisdn,
            "countrycode": config("COUNTRYCODE"),
            "cli": config("CLI"),
            "messagetype": config("MESSAGE_TYPE"),
            "message": message,
            "clienttransid": config("CLIENTTRANSID"),
            "bill_msisdn": config("BILLMSISDN"),
            "tran_type": "T",
            "request_type": "S",
            "rn_code": "71",
        }

        response = requests.post(config("API_URL"), headers=headers, json=payload)
        response_json = response.json()
        return response_json
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

