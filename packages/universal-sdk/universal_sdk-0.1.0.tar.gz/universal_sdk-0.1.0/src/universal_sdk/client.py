import os
import requests
from .exceptions import APIError

class Client:
    def __init__(self, base_url: str = None, api_key: str = None, upload_folder: str = None):
        """
        Universal SDK Client for the File Text Extractor API
        """
        self.base_url = base_url or os.getenv("API_BASE_URL", "http://localhost:8000")
        self.api_key = api_key or os.getenv("API_KEY", "")
        self.upload_folder = upload_folder or os.getenv("UPLOAD_FOLDER", "uploads")

    def _headers(self):
        headers = {"accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def upload_file(self, file_path: str):
        """
        Uploads a PDF or CSV file to the API and returns the extracted data.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        url = f"{self.base_url}/upload"

        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f, "application/octet-stream")}
            response = requests.post(url, headers=self._headers(), files=files)

        if response.status_code != 200:
            raise APIError(f"Error {response.status_code}: {response.text}")

        return response.json()
