import uuid
from datetime import datetime

import pytz


class DatabaseAccess:
    def __init__(self, db):
        self.db = db

    def get_fingerprint(self, fingerprint):
        print('Not implemented')

    def add_log(self, hash, user):
        print('Not implemented')

    def get_user(self, id):
        print('Not implemented')


class FirebaseAccess(DatabaseAccess):

    def get_fingerprint(self, fingerprint):
        print('Searching fingerprint in firebase')
        return self.db.reference('fingerprints/' + fingerprint).get()

    def add_log(self, hash, user):
        print('Adding remote log')

        time = datetime.now(tz=pytz.timezone("America/Argentina/Cordoba")).isoformat("T")

        logs_ref = self.db.reference('logs')

        if user:
            user_id = user['user']
        else:
            user_id = ''
        logs_ref.push({
            'datetime': str(time),
            'hash': hash,
            'user': user_id
        })

    def get_user(self, id):
        user_found = self.db.reference('users/' + id).get()
        return user_found


def create_log_data(hash_data, user, log_id):
    time = datetime.now(tz=pytz.timezone("America/Argentina/Cordoba")).isoformat("T")
    log_data = {
        "datetime": str(time),
        "hash": hash_data,
        "user": user,
        "_id": log_id
    }
    return log_data


class MongoAccess(DatabaseAccess):

    def get_fingerprint(self, fingerprint):
        print('Searching fingerprint in local db')
        finger_db = self.db.fingerprints
        return finger_db.find_one({'fingerprint': fingerprint})

    def add_log(self, hash, user_id):
        print('Adding local log')
        log_data = create_log_data(hash, user_id, uuid.uuid1())

        logs_db = self.db.logs
        logs_db.insert_one(log_data)
