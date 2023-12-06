import os

from bson.json_util import dumps
import pymongo

from flask import Flask, request

from src.db import get_db


app = Flask(__name__)
app.config["PAGE_LIMIT"] = 25


@app.route("/")
def test():
    """Livliness test/Hello World!"""

    return "Hello World! This is a Flask app."


@app.route("/plugins")
def plugins():
    """
    List of plugins with basic info. Paginated via query string, and sorted by name by default.

    Valid query string parameters:
        - page: int
        - sort: str (name, stars, last_updated) default: stars
        - desc: bool  default: true
    """
    page = request.args.get("page", 1, type=int)
    sort = request.args.get("sort", "stars", type=str)
    desc = request.args.get("desc", True, type=bool)

    app.logger.debug(f"page: {page}, sort: {sort}, desc: {desc}")

    # validate page
    if sort not in ["name", "stars", "last_updated"]:
        return "Invalid sort parameter", 400

    # get repos
    db = get_db()
    repos = (
        db["repos"].find().sort(sort, pymongo.DESCENDING if desc else pymongo.ASCENDING)
    )
    if page > 1: # handle page request
        repos = repos.skip((page - 1) * app.config["PAGE_LIMIT"])
    repos = repos.limit(app.config["PAGE_LIMIT"])

    # extract only relevant info
    res = [
        {
            "name": x["name"],
            "description": x["description"],
            "url": x["url"],
            "stars": x["stars"],
            "author": x["author"],
            "last_updated": x["last_updated"],
        }
        for x in repos
    ]

    return dumps(res)

@app.route("/plugins/<name>")
def plugin_details(name):
    """
    Get plugin info by name.
    """
    db = get_db()
    repo = db["repos"].find_one({"name": name})
    if repo is None:
        return "Plugin not found", 404

    repo.pop("_id")
    repo.pop("id")
    return dumps(repo)

@app.route("/plugins/search")
def plugin_search():
    """
    Search for plugins by name. 
    """
    query = request.args.get("q", "", type=str)
    db = get_db()
    repos = db["repos"].find({"name": {"$regex": query, "$options": "i"}}).limit(15)
    res = [
        {
            "name": x["name"],
            "description": x["description"],
            "url": x["url"],
            "stars": x["stars"],
        }
        for x in repos
    ]
    return dumps(res)


# main
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
