import os, sys

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from flask_pymongo.wrappers import Database

from pymongo.errors import OperationFailure

from flask import g, current_app


def get_db() -> Database:
    """
    Configuration method to return db instance
    """
    db = getattr(g, "_database", None)
    if db is None:
        db_username = os.environ.get("DB_USERNAME")
        db_password = os.environ.get("DB_PASSWORD")

        if not db_username or not db_password:
            raise ValueError("Missing DB_USERNAME or DB_PASSWORD environment variable")
        uri = (
            f"mongodb+srv://{db_username}:{db_password}@nvim-plugin-list.kuxk7uc.mongodb.net/"
            "?retryWrites=true&w=majority"
        )

        # setup db connection
        client = MongoClient(
            uri, server_api=ServerApi("1"), uuidRepresentation="standard"
        )
        try:
            client.admin.command("ping", check=True)
            current_app.logger.info("Successfully connected to the Atlas Cluster")
        except OperationFailure as e:
            current_app.logger.error(
                "Unable to connect to the Atlas Cluster, error:", str(e)
            )
            raise e

        db = g._database = client["repos"]
    return db
