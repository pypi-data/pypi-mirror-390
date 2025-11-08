import requests
from .reqsession import reqsession, Advreqsession
from bs4 import BeautifulSoup
import json
import os
import asyncio
import math

class GoClient:
    def __init__(self, api_key = None):
        self.api_key = api_key or os.environ['gofiles_key'] or None
    def upload_video(self, file_path: str, folder_id=None):
        '''
        client = GoClient()
        client.upload_video(file_path, folder_id)
        ```json
        {
            "status": "ok",
            "data": {
                "downloadPage": "https://gofile.io/d/Z19n9a",
                "code": "Z19n9a",
                "parentFolder": "3dbc2f87-4c1e-4a81-badc-af004e61a5b4",
                "fileId": "4991e6d7-5217-46ae-af3d-c9174adae924",
                "fileName": "example.mp4",
                "md5": "10c918b1d01aea85864ee65d9e0c2305"
            }
        }
  New
  {
  "status": "ok",
  "data": {
    "createTime": 1730723301,
    "downloadPage": "https://gofile.io/d/grgw9m",
    "id": "88013803-fc9d-4750-b8bb-3cfb0b3acd63",
    "md5": "398bd8f9f5bfb9bd24bd881ff7f1e393",
    "mimetype": "image/jpeg",
    "modTime": 1730723301,
    "name": "photo_2024-10-23_06-32-53_7433399967630229508.jpg",
    "parentFolder": "f4beda51-f177-4cf1-80d6-6f8b143cd4db",
    "parentFolderCode": "grgw9m",
    "servers": [
      "store3"
    ],
    "size": 241408,
    "type": "file"
  }
}
        ```
        '''
        try:
            upload_url = get_go_server()
            data = {}
            if folder_id:
                data["folderId"] = folder_id
            if self.api_key:
                data["token"] = self.api_key
            files = {'file': open(file_path, 'rb')}
            response = requests.post(upload_url, files=files, data=data)
            data_f = json.loads(response.text)
            return data_f
        except requests.exceptions.RequestException as e:
            print("Request Exception:", e)
            return f"Error {e}"

def get_go_server():
    api = "https://api.gofile.io/servers"
    response = Advreqsession(api)
    json_data = json.loads(response.text)
    server_id = json_data["data"]["servers"][0]["name"]
    upload_url = f"https://{server_id}.gofile.io/contents/uploadfile"
    return upload_url

"""
from heartloglost import GoClient

gofiles_key = os.environ['gofiles_key']

File_Path = "/content/vid/[S5-E10] [480p] Date A Live  [Sub] @Anime_A.mkv" # @param {type:"string"}
Folder_id = ""

client = GoClient(gofiles_key)
data = client.upload_video(File_Path, Folder_id)
print("dddd"+f"{data}")
"""
# Output = 
"""
{'data': {'code': 'OUs3ex',
  'downloadPage': 'https://gofile.io/d/OUs3ex',
  'fileId': '86db1cd8-ba88-4dd7-9377-c219008b2dac',
  'fileName': '[S5-E10] [480p] Date A Live  [Sub] @Anime_A.mkv',
  'md5': '8dc6420b7fa951c48bf0ca5ddcb41eff',
  'parentFolder': '89195d85-2014-4786-b3eb-e07d5c1528ee'},
 'status': 'ok'}
"""