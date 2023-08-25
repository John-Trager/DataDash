"""
A network file server
"""
import os
from pathlib import Path
from flask import Flask, request
from flask_dropzone import Dropzone

DST_DIR = "/Users/jt-lab/Projects/DashData/dst_data"

app = Flask(__name__)

dropzone = Dropzone(app)


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        f = request.files.get("file")
        f.save(os.path.join(DST_DIR, f.filename))

    return "upload template"


if __name__ == "__main__":
    # insure that the dst folder, make it if it doesn't
    Path(DST_DIR).mkdir(parents=True, exist_ok=True)

    app.run(port=8001, debug=True)
