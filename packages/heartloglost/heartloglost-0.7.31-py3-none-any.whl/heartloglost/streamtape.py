import requests
from .reqsession import reqsession, Advreqsession
from bs4 import BeautifulSoup
import json
import os
import asyncio
import math

class STClient:
    def __init__(self, username = None, api_key = None):
        self.username = username or os.environ['streamtape_login']
        self.api_key = api_key or os.environ['streamtape_key']
    def auth(self):
        if not all((self.username, self.api_key)):
            raise ValueError("Username, password, and API key must be specified.")
        Api_info = f"https://api.streamtape.com/account/info?login={self.username}&key={self.api_key}"
        try:
            response = Advreqsession(Api_info)
            # response.raise_for_status()  # Raise an exception if the request was not successful
            json_data = json.loads(response.text)
            a_api = json_data["status"]
            if int(a_api) == 200:
                print("You are authorised")
            else:
                print("Unsuccessful ! Check credentials.")
        except Exception as e:
            print(e)

    def upload_video(self, file_path: str, folder_id=None):
        '''
        client.upload_video(file_path, folder_id)
        '''
        try:
            Main_API = f"https://api.streamtape.com/file/ul?login={self.username}&key={self.api_key}"
            payload = {}
            if folder_id:
                payload["folder"] = folder_id
            response = Advreqsession(Main_API, params=payload)
            # response.raise_for_status()  # Raise an exception if the request was not successful
            json_data = json.loads(response.text)
            temp_api = json_data["result"]["url"]
            print("Temp URL:" + temp_api)
            files = {'file': open(file_path, 'rb')}
            response = requests.post(temp_api, files=files)
            # response.raise_for_status()
            data_f = json.loads(response.text)
            download_link = data_f["result"]["url"]
            print(download_link)
            return download_link
        except requests.exceptions.RequestException as e:
            print("Request Exception:", e)
            return f"Error {e}"

    def tapeimg_url(url):
        try:
            response = Advreqsession(url)
            # response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            og_image_tag = soup.find('meta', {'name': 'og:image'})
            if og_image_tag:
                image_url = og_image_tag['content']
                return image_url
            else:
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def add_remote(self, url: str, folder_id=None, name=None):
        '''
        client.add_remote(url: str, folder_id, name: str)
        '''
        # Main_API = f"https://api.streamtape.com/file/ul?login={self.username}&key={self.api_key}&folder={self.folder_id}"
        if url:
            try:
                Main_API = f"https://api.streamtape.com/remotedl/add?login={self.username}&key={self.api_key}&url={url}"
                payload = {}
                if name:
                    payload["name"] = name
                if folder_id:
                    payload["folder"] = folder_id
                response = Advreqsession(Main_API, params=payload)
                # response.raise_for_status()  # Raise an exception if the request was not successful
                json_data = json.loads(response.text)
                remote_id = json_data["result"]["id"]
                print("UpID:" + remote_id)
                return remote_id
            except requests.exceptions.RequestException as e:
                print("Request Exception:", e)
                return f"Error {e}"
        else:
            return "Please Give Api Key/url/"

    # check out docs\streamtape_gud\remotestatus.md
    def remote_status(self, id):
        '''
        ## Usage
        client.remote_status(remote_id)

        ## Response
        ```json
        {
        "status": 200,
        "msg": "OK",
        "result": {
            "LnvnE51P5gc": {
                "id": "LnvnE51P5gc",
                "remoteurl": "https://vid.me/myvideo123",
                "status": "new",
                "bytes_loaded": null,
                "bytes_total": null,
                "folderid": "LnvnE51P5gc",
                "added": "2019-12-31 23:59:59",
                "last_update": "2019-12-31 23:59:59",
                "extid": false,
                "url": false
            }
        }
        }
        ```
        '''
        if id:
            try:
                Main_API = f"https://api.streamtape.com/remotedl/status?login={self.username}&key={self.api_key}&id={id}"
                payload = {}
                response = Advreqsession(Main_API, params=payload)
                # response.raise_for_status()  # Raise an exception if the request was not successful
                json_data = json.loads(response.text)
                # print("UpID:" + json_data)
                return json_data
            except requests.exceptions.RequestException as e:
                print("Request Exception:", e)
                return f"Error {e}"
        else:
            return "Please Give id and what to get"

# idd = "FVAaYwD_ULM"
# json_res = client.remote_status("FVAaYwD_ULM")
# a = client.remote_status("J4Cx7hXoT1s")
# print(a["status"])
    def file_info(self, file_id):
        '''
        ## Usage 
        client.file_info(file_id)
        ## Response
        ```json
        {
            "status": 200,
            "msg": "OK",
            "result": {
                "wkzYeyVpdyuem9": {
                    "id": "wkzYeyVpdyuem9",
                    "status": 200,
                    "name": "hdidhk.mp4",
                    "size": 197065376,
                    "converted": True,
                    "thumb": "https://thumb.tapecontent.net/thumb/wkzYeyVpdyuem9/kwLzMwjxgofee0.jpg"
                }
            }
        }
        ```json
        ## Failed 
        ```json
        {
            "status": 200,
            "msg": "OK",
            "result": {
                "d7Z7BjY9DDskVVK": {
                    "id": "d7Z7BjY9DDskVVK",
                    "status": 404,
                    "name": False,
                    "size": 0,
                    "converted": False
                }
            }
        }
        ```
        '''
        if file_id:
            try:
                Main_API = f"https://api.streamtape.com/file/info?login={self.username}&key={self.api_key}&file={file_id}"
                payload = {}
                response = Advreqsession(Main_API, params=payload)
                # response.raise_for_status()  # Raise an exception if the request was not successful
                json_data = json.loads(response.text)
                # print("UpID:" + json_data)
                return json_data
            except requests.exceptions.RequestException as e:
                print("Request Exception:", e)
                return f"Error {e}"
        else:
            return "Please Give id and what to get"
        
    def rename_file(self, file_id, name):
        if file_id and name:
            try:
                Main_API = f"https://api.streamtape.com/file/rename?login={self.username}&key={self.api_key}&file={file_id}&name={name}"
                payload = {}
                response = Advreqsession(Main_API, params=payload)
                # response.raise_for_status()  # Raise an exception if the request was not successful
                json_data = json.loads(response.text)
                return json_data
            except requests.exceptions.RequestException as e:
                print("Request Exception:", e)
                return f"Error {e}"
        else:
            return "Please provide id and name."
    def delete_file(self, file_id):
        if file_id:
            try:
                Main_API = f"https://api.streamtape.com/file/delete?login={self.username}&key={self.api_key}&file={file_id}"
                payload = {}
                response = Advreqsession(Main_API, params=payload)
                # response.raise_for_status()  # Raise an exception if the request was not successful
                json_data = json.loads(response.text)
                return json_data
            except requests.exceptions.RequestException as e:
                print("Request Exception:", e)
                return f"Error {e}"
        else:
            return "Please provide id."
    def add_folder(self, name=None, pid=None):
        '''
        Add a folder to the specified parent folder.

        Parameters:
        - name (str): The name of the folder.
        - pid (str): The ID of the parent folder.

        Usage:

        ```py
        client.add_remote(file_id, name, pid)
        ```
        '''
        if name:
            try:
                Main_API = f"https://api.streamtape.com/file/createfolder?login={self.username}&key={self.api_key}&name={name}"
                payload = {}
                if pid:
                    payload["pid"] = pid  # Parent folder
                response = Advreqsession(Main_API, params=payload)
                # response.raise_for_status()  # Raise an exception if the request was not successful
                json_data = json.loads(response.text)
                FolderId = json_data["result"]["folderid"]
                print(f"Folder {name}:" + FolderId)
                return FolderId
            except requests.exceptions.RequestException as e:
                print("Request Exception:", e)
                return f"Error {e}"
        else:
            return "Please Give Api Key/url/"
    def delete_folder(self, folder_id):
        if folder_id:
            try:
                Main_API = f"https://api.streamtape.com/file/deletefolder?login={self.username}&key={self.api_key}&folder={folder_id}"
                payload = {}
                response = Advreqsession(Main_API, params=payload)
                # response.raise_for_status()  # Raise an exception if the request was not successful
                json_data = json.loads(response.text)
                return json_data
            except requests.exceptions.RequestException as e:
                print("Request Exception:", e)
                return f"Error {e}"
        else:
            return "Please provide id."
    def list_files(self, parent_folder_id=None):
        try:
            Main_API = f"https://api.streamtape.com/file/listfolder?login={self.username}&key={self.api_key}"
            payload = {}
            if parent_folder_id:
                payload["folder"] = parent_folder_id  # Parent folder
            response = Advreqsession(Main_API, params=payload)
            # response.raise_for_status()  # Raise an exception if the request was not successful
            json_data = json.loads(response.text)
            return json_data
        except requests.exceptions.RequestException as e:
            print("Request Exception:", e)
            return f"Error {e}"


def st_url_id(url):
    """
    st_url_id(url) `url or id`
    """
    if url.startswith("http"):
        return url.split("/", 5)[4]
    else:
        return url

def add_parm(dicti, name, value):
    dicti[f"{name}"] = value

# Example usage:
# client = STClient("your_username", "your_api_key")
# client.auth()
# client.upload_video("path_to_video.mp4", "folder_id")
