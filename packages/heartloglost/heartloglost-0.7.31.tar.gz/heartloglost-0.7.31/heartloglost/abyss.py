import requests
import json
import os
import asyncio
import math

'''
class AbyssClient:
    def __init__(self, api_url = None):
        self.api_url = api_url or os.environ['api_url'] or None
    def upload_video(self, file_path: str, file_name = None, ):
'''
  
'''
        try:
            upload_url = self.api_url
            data = {}
            if self.api_key:
                data["token"] = self.api_key
            files = {'file': open(file_path, 'rb')}
            response = requests.post(upload_url, files=files, data=data)
            data_f = json.loads(response.text)
            return data_f
        except requests.exceptions.RequestException as e:
            print("Request Exception:", e)
            return f"Error {e}"
'''

import requests
import os
import sys

# Define a custom exception
class AbyssAPIError(Exception):
    """Custom exception for API errors."""
    pass

class AbyssClient:
    """
    calling login() with email/password to get a session token.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initializes the client.
        
        :param api_key: Your Abyss.to API Key. If not provided,
                        it will check the 'ABYSS_API_KEY' environment variable.
        """
        self.api_key = api_key or os.environ.get('ABYSS_API_KEY')
        self.token = None
        
        self.base_api_url = "https://api.abyss.to/v1"
        self.auth_api_url = "https://api.abyss.to/auth"
        self.upload_api_url = "http://up.abyss.to"
        
        self.session = requests.Session()

    def login(self, email: str, password: str):
        """
        Logs in using email and password to get a JWT token.
        This token will be used for subsequent requests.
        """
        url = f"{self.auth_api_url}/login"
        try:
            response = self.session.post(url, json={"email": email, "password": password})
            response.raise_for_status()
            
            data = response.json()
            self.token = data.get('token')
            
            if not self.token:
                raise AbyssAPIError("Login failed, token not found in response.")
            
            self.api_key = None  # Clear API key as we are using token auth
            return data
            
        except requests.exceptions.HTTPError as err:
            raise AbyssAPIError(f"Login failed: {err.response.status_code} - {err.response.text}") from err
        except requests.exceptions.RequestException as err:
            raise AbyssAPIError(f"Login request failed: {err}") from err

    def _make_request(self, method: str, endpoint: str, params: dict = None, json_data: dict = None):
        """Helper method for making authenticated requests to the v1 API."""
        
        url = f"{self.base_api_url}/{endpoint}"
        headers = {}
        qparams = params or {}

        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        elif self.api_key:
            qparams['key'] = self.api_key
        else:
            raise AbyssAPIError("Client not authenticated. Provide an api_key or call login().")

        try:
            response = self.session.request(method, url, headers=headers, params=qparams, json=json_data)
            response.raise_for_status()
            
            # DELETE requests might not return JSON
            if response.status_code == 204 or not response.content:
                return {"success": True}
                
            return response.json()
            
        except requests.exceptions.HTTPError as err:
            raise AbyssAPIError(f"API Error: {err.response.status_code} - {err.response.text}") from err
        except requests.exceptions.RequestException as err:
            raise AbyssAPIError(f"Request Error: {err}") from err

    def upload_video(self, file_path: str, file_name: str = None):
        """
        Uploads a video file.
        This endpoint requires an API Key and does not work with token auth.
        """
        if not self.api_key:
            raise AbyssAPIError("File upload requires an api_key. Token auth is not supported for this endpoint.")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at {file_path}")

        upload_filename = file_name or os.path.basename(file_path)
        upload_url = f"{self.upload_api_url}/{self.api_key}"

        try:
            with open(file_path, 'rb') as f:
                files = {'file': (upload_filename, f)}
                response = requests.post(upload_url, files=files)
                response.raise_for_status()
                return response.json()

        except requests.exceptions.HTTPError as err:
            raise AbyssAPIError(f"Upload failed: {err.response.status_code} - {err.response.text}") from err
        except requests.exceptions.RequestException as e:
            raise AbyssAPIError(f"Upload request failed: {e}") from e

    # --- About ---
    def get_about(self):
        """Gets quota and account information."""
        return self._make_request('GET', 'about')

    # --- Resources ---
    def list_resources(self, folder_id: str = None, search_type: str = None, keyword: str = None,
                       resource_type: str = None, max_results: int = None, order_by: str = None,
                       page_token: str = None):
        """Get resources (files and folders)."""
        params = {
            "folderId": folder_id,
            "searchType": search_type,
            "keyword": keyword,
            "type": resource_type,
            "maxResults": max_results,
            "orderBy": order_by,
            "pageToken": page_token
        }
        # Filter out None values
        params = {k: v for k, v in params.items() if v is not None}
        return self._make_request('GET', 'resources', params=params)

    # --- Files ---
    def get_file_info(self, file_id: str):
        """Get info for a specific file."""
        return self._make_request('GET', f'files/{file_id}')

    def update_file_info(self, file_id: str, name: str):
        """Update a file's name."""
        return self._make_request('PUT', f'files/{file_id}', json_data={"name": name})

    def move_file(self, file_id: str, parent_id: str = None):
        """Move a file to a different folder."""
        params = {"parentId": parent_id} if parent_id else {}
        return self._make_request('PATCH', f'files/{file_id}', params=params)

    def delete_file(self, file_id: str):
        """Delete a file."""
        return self._make_request('DELETE', f'files/{file_id}')

    # --- Folders ---
    def create_folder(self, name: str, parent_id: str = None):
        """Create a new folder."""
        data = {"name": name}
        if parent_id:
            data["parentId"] = parent_id
        return self._make_request('POST', 'folders', json_data=data)

    def list_folders(self, folder_id: str = None, keyword: str = None, 
                     max_results: int = None, order_by: str = None, page_token: str = None):
        """Get a list of folders."""
        params = {
            "folderId": folder_id,
            "keyword": keyword,
            "maxResults": max_results,
            "orderBy": order_by,
            "pageToken": page_token
        }
        params = {k: v for k, v in params.items() if v is not None}
        return self._make_request('GET', 'folders/list', params=params)

    def get_folder_info(self, folder_id: str):
        """Get info for a specific folder."""
        return self._make_request('GET', f'folders/{folder_id}')

    def update_folder(self, folder_id: str, name: str):
        """Update a folder's name."""
        return self._make_request('PUT', f'folders/{folder_id}', json_data={"name": name})

    def move_folder(self, folder_id: str, parent_id: str = None):
        """Move a folder into another folder."""
        params = {"parentId": parent_id} if parent_id else {}
        return self._make_request('PATCH', f'folders/{folder_id}', params=params)

    def delete_folder(self, folder_id: str):
        """Delete a folder."""
        return self._make_request('DELETE', f'folders/{folder_id}')

    # --- Subtitles ---
    def list_subtitles(self, file_id: str):
        """Get list of subtitles for a file."""
        return self._make_request('GET', f'subtitles/{file_id}/list')

    def delete_subtitle(self, subtitle_id: str):
        """Delete a subtitle."""
        return self._make_request('DELETE', f'subtitles/{subtitle_id}')

    # Note: Upload subtitle is more complex and not included in this basic client.
    # It requires a PUT request with application/octet-stream and raw binary data.

