"""
A client that can be used to upload files to the server
"""

import requests


url = "http://localhost:8001/upload"
file_path = "/Users/jt-lab/Projects/DashData/storage_server/test.txt"

with open(file_path, "rb") as file:
    response = requests.post(url, files={"file": file})

print(response.text)
