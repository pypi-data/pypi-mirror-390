import requests
from .reqsession import reqsession, Advreqsession
from bs4 import BeautifulSoup
import json
import os
import base64
import asyncio
import math

# = None

class FileioClient:
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
            upload_url = "https://file.io/"
            
            files = {'file': open(file_path, 'rb')}
            response = requests.post(upload_url, files=files)
            data_f = json.loads(response.text)
            return data_f
        except requests.exceptions.RequestException as e:
            print("Request Exception:", e)
            return f"Error {e}"

