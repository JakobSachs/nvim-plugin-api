import os

from bson.json_util import dumps
from bson.regex import Regex
import pymongo

from flask import Flask, request

from src.db import get_db


app = Flask(__name__)
app.config["PAGE_LIMIT"] = 25


@app.route("/")
def test():
    """Livliness test/Hello World!"""

    return "Hello World! This is a Flask app."


@app.route("/languages")
def languages():
    """
    List of all languages used in plugins. Sorted by repo count.
    """

    db = get_db()
    languages = db["repo"].aggregate(
        [
            {
                "$group": {
                    "_id": "$language",  # Group by the 'language' field
                    "count": {"$sum": 1},  # Count the number of documents in each group
                }
            }
        ]
    )
    languages = sorted(languages, key=lambda x: x["count"], reverse=True)
    # filter out ones with less then 20 repos
    languages = [x for x in languages if x["count"] >= 5]

    return dumps(languages)


@app.route("/plugins")
def plugins():
    """
    List of plugins with basic info. Paginated via query string, and sorted by name by default.

    Valid query string parameters:
        - page: int
        - sort: str (name, stars, last_updated) default: stars
        - desc: bool  default: true
        - search: str
    """

    # Handle page and sorting
    page = request.args.get("page", 1, type=int)

    sort = request.args.get("sort", "stars", type=str)

    # Handle and validate desc
    desc_str: str = request.args.get("desc", "True", type=str)
    desc: bool = False
    if desc_str.lower() == "true":
        desc = True
    elif desc_str.lower() == "false":
        desc = False
    else:
        return "Invalid desc parameter", 400

    # Handle search
    # TODO: make search more fuzzy and escape regex
    search = request.args.get("search", "", type=str)
    # Modify query to include universal search filter
    search_filter = {}
    if search:
        regex_search = Regex(search, "i")  # 'i' for case-insensitive
        search_filter = {
            "$or": [
                {"name": regex_search},
                {"description": regex_search},
                {"author": regex_search}
                # Add other searchable fields here
            ]
        }

    app.logger.debug(f"page: {page}, sort: {sort}, desc: {desc}")

    # validate
    if sort not in ["name", "stars", "last_updated"]:
        return "Invalid sort parameter", 400

    # get repos
    db = get_db()
    repos = (
        db["repo"]
        .find(search_filter)
        .sort(sort, pymongo.DESCENDING if desc else pymongo.ASCENDING)
    )
    if page > 1:  # handle page request
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
            "language": x["language"],
            "last_updated": x["last_updated"],
        }
        for x in repos
    ]

    return dumps(res)


@app.route("/plugin/<author>/<name>")
def plugin_details(author, name):
    """
    Get plugin info by author and name.
    """
    db = get_db()
    repo = db["repo"].find_one({"author": author, "name": name})
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
    repos = db["repo"].find({"name": {"$regex": query, "$options": "i"}}).limit(15)
    res = [
        {
            "name": x["name"],
            "description": x["description"],
            "url": x["url"],
            "stars": x["stars"],
            "readme": x["readme"] if "readme" in x else "",
        }
        for x in repos
    ]
    return dumps(res)


# main
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
