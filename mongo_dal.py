from pymongo import MongoClient
from pymongo.errors import InvalidOperation, ConnectionFailure
import os
from flask import abort

MONGO_ADDRESS = os.environ['MONGO_DB_LOCATION']

class MongoDAO:
    """" Data Access Object class for use with MongoDB"""
    def __init__(self):
        self.client = MongoClient(MONGO_ADDRESS)
        self.db = self.client['IFR']
        self.users = self.db['users']
        self.file_counter = self.db['counters']
        try:
            self.client.admin.command('ismaster')
        except ConnectionFailure:
            print('Database is not available')
            abort(503, 'Database is not available')

    def add_user(self, user_id, room_list, name=None):
        user = {'_id': user_id,
                'name': name,
                'access_areas': room_list}
        try:
            self.users.insert_one(user)
        except InvalidOperation:
            return False
        return True

    def find_user(self, user_id):
        user = self.users.find_one({'_id': user_id})
        if not user:
            return False
        return user

    def remove_user(self, user_id):
        self.users.remove(user_id)

    def remove_all(self):
        self.users.remove()

    def get_file_counter(self):
        counter = self.file_counter.find_one({'name': 'file_counter'})
        if not counter:
            return False
        val = counter['value']
        try:
            self.file_counter.update_one({'name': 'file_counter'}, {'$inc':{'value': 1}})
        except InvalidOperation:
            return False
        return val
