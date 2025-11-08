import requests
from .reqsession import reqsession, Advreqsession
from bs4 import BeautifulSoup
import json
import os
import base64
import asyncio
import math

# = None

class PixClient:
    def __init__(self, api_key = None):
        self.api_key = api_key or os.environ['gofiles_key'] or None
    def upload(self, file_path: str=None, name :str=None, anon=True):
        '''
        client = GoClient()
        client.upload(file_path, folder_id)
        ```json
        {
        "success": true,
        "id": "abc123" // ID of the newly uploaded file
        }
        ```
        '''
        try:
            upload_url = "https://pixeldrain.com/api/file/"
            data = {}
            data["anonymous"]=True if anon is True else False
            if name:
                data["name"] = name
            if self.api_key:
                data["Authorization"] = "Basic " + base64.b64encode(f":{self.api_key}".encode()).decode()
            files = {'file': open(file_path, 'rb')}
            response = requests.post(upload_url, files=files, data=data)
            data_f = json.loads(response.text)
            return data_f
        except requests.exceptions.RequestException as e:
            print("Request Exception:", e)
            return f"Error {e}"

