import requests
from .reqsession import reqsession
from bs4 import BeautifulSoup
import json
import os
import asyncio
import math

class FLClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ['flapi_key']
    def auth(self):
        if not all((self.api_key)):
            raise ValueError("API key must be specified.")
        Api_info = f"https://api.filelions.com/api/account/info?key={self.api_key}"
        try:
            response = reqsession(Api_info)
            response.raise_for_status()  # Raise an exception if the request was not successful
            json_data = json.loads(response.text)
            a_api = json_data["status"]
            if int(a_api) == 200:
                print("You are authorised")
            else:
                print("Unsuccessful ! Check credentials.")
        except Exception as e:
            print(e)

    def upload_video(self, file_path, folder_id=13026):
        Main_API = f"https://api.filelions.com/api/upload/server?key={self.api_key}"
        try:
            response = reqsession(Main_API)
            response.raise_for_status()  # Raise an exception if the request was not successful
            json_data = json.loads(response.text)
            temp_api = json_data["result"]
            print("Temp URL:" + temp_api)
            data = {
                'key': str(self.api_key),
                'fld_id': folder_id
            }
            files = {'file': open(file_path, 'rb')}
            try:
                response = requests.post(temp_api, data=data, files=files)
            except Exception as e:
                print("excp:",e)
            print(response.text)
            response.raise_for_status()
            data_f = json.loads(response.text)
            filecode = data_f["files"][0]["filecode"]
            return filecode
        except requests.exceptions.RequestException as e:
            print("Request Exception:", e)
            return f"Error {e}"


def extract_filecodes_from_json(response_json, base_url="https://filelions.online/d/"):
    try:
        # Parse the JSON string
        if isinstance(response_json, dict):
            data = response_json
        else:
            # Parse the JSON string
            data = json.loads(response_json.text)

        # Extract the "filecode" values and prepend the base_url
        filecodes = [base_url + file['filecode'] for file in data['files']]

        return filecodes
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return []


# from heartloglost import FLClient as FL
# FL.auth(api_key)
# FL.upload_video(file_path, folder_id=13026)