from pathlib import Path
import requests
import zipfile
import io
import os

buffer = io.BytesIO()

with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
    for root, dirs, files in os.walk("."):
        for file in files:
            zip_file.write(Path(root) / file)

buffer.seek(0)

response = requests.post("http://127.0.0.1:8000/publish", files={"file": (Path.cwd().name + ".zip", buffer, "application/zip")})

print(response.status_code)
print(response.json())