import os

from bson.json_util import dumps

from db import get_db

from flask import Flask
app = Flask(__name__)


@app.route("/")
def hello_world():
    """Example Hello World route."""
    db = get_db()
    test = db["repos"].find_one()

    return test["name"]



# main
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
