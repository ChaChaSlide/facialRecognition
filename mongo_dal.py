from pymongo import MongoClient
from pymongo.errors import InvalidOperation


class MongoDAO:
    def __init__(self):
        self.client = MongoClient('mongodb+srv://Admin:openpass@cluster0-dxfvh.gcp.mongodb.net/test?retryWrites=true')
        self.db = self.client['IFR']
        self.users = self.db['users']
        self.file_counter = self.db['counters']

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
        self.db.drop_collection(self.user)
        self.db.create_collection('user')

    def get_file_counter(self):
        counter = self.file_counter.find_one({'name': 'file_counter'})
        if not counter:
            return False
        val = counter['value']
        counter['value'] = val+1
        try:
            self.file_counter.update(counter)
        except InvalidOperation:
            return False
        return val
