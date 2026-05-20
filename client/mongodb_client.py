import os
from logging import exception
from functools import wraps

from dotenv import load_dotenv

from pymongo import MongoClient
from pymongo.server_api import ServerApi

import util
import asyncio

load_dotenv()
uri=os.getenv("DB_URI")
client = MongoClient(uri)

class DataBase_tab:
    def __init__(self,db,collection):
        self.db = client[db]
        self.collection = self.db[collection]
        self.pinged = False

    def ping(self):
        try:
            client.admin.command('ping')
            self.pinged = True
        except Exception as e:
            print(e)
            self.pinged = False

    def check_db(func):
        @wraps(func)
        # 2. Because it's an async method, the wrapper must be async
        async def wrapper(self, *args, **kwargs):
            if not self.pinged:
                self.ping()
            if not self.pinged:
                raise util.MissingDBError("fail to ping db")
            # 3. Await the original async method, passing self and args
            return await func(self, *args, **kwargs)
        return wrapper

    @check_db
    async def insert(self,data):
        try:
            result = self.collection.insert_one(data)
            return result.inserted_id
        except Exception as e:
            print(e)
            return None

    @check_db
    async def get_single(self,query):
        # example {"status": "active"}
        try:
            single_doc = self.collection.find_one(query)
            return single_doc
        except Exception as e:
            print(e)
            return None

    @check_db
    async def get_many(self,query):
        # example {"age": {"$gt": 25}}
        try:
            cursor = self.collection.find(query)
            return cursor
        except Exception as e:
            print(e)
            return None
