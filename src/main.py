import os
import json


from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello_world():
    """Example Hello World route."""

    print(app.db["repos"].find_one())



    # main
if __name__ == "__main__":
    
    db_username = os.environ.get("DB_USERNAME")
    db_password = os.environ.get("DB_PASSWORD")

    if not db_username or not db_password:
        raise ValueError("Missing DB_USERNAME or DB_PASSWORD environment variable")

    app.config["MONGO_URI"] = (
        f"mongodb+srv://{db_username}:{db_password}@nvim-plugin-list.kuxk7uc.mongodb.net/"
        "?retryWrites=true&w=majority"
    )

    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
