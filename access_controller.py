from datetime import datetime

import firebase_admin
import pytz
from firebase_admin import credentials
from firebase_admin import db
import urllib.request as urllib2
from pymongo import MongoClient
import uuid


def search_fingerprint_firebase(fingerprint):
    print('Searching fingerprint in firebase')
    return db.reference('fingerprints/' + fingerprint).get()


def add_fingerprint(fingerprint, user):
    print('Adding new fingerprint for ', user)  # TODO validar si la huella existe
    fingerprint_ref = db.reference('fingerprints/')
    user_id = None
    for key, value in user.items():
        user_id = key

    fingerprint_ref.child(fingerprint).set({
        'user': user_id
    })


def search_fingerprint_local(fingerprint, local_db):
    print('Searching fingerprint in local db')
    finger_db = local_db.fingerprints
    return finger_db.find_one({'_id': fingerprint})


def authenticate():
    cred = credentials.Certificate("google_credentials.json")
    firebase_admin.initialize_app(cred, options={
        'databaseURL': 'https://cda-bithouse.firebaseio.com/',
    })


def add_log_firebase(hash, user):
    print('Adding remote log')

    time = datetime.now(tz=pytz.timezone("America/Argentina/Cordoba")).isoformat("T")

    logs_ref = db.reference('logs')

    if user:
        user_id = user['user']
    else:
        user_id = ''
    logs_ref.push({
        'datetime': str(time),
        'hash': hash,
        'lastname': '',  # TODO
        'name': '',
        'user': user_id
    })


def add_log_local(user, hash, user_id, local_db):
    print('Adding local log')
    log_data = create_log_data(hash, user_id, '', '', uuid.uuid1())  # TODO

    logs_db = local_db.logs
    logs_db.insert_one(log_data)


def create_log_data(hash_data, user, name, lastname, log_id):
    time = datetime.now(tz=pytz.timezone("America/Argentina/Cordoba")).isoformat("T")
    log_data = {
        "datetime": str(time),
        "hash": hash_data,
        "user": user,
        "name": name,
        "lastname": lastname,
        "_id": log_id
    }
    return log_data


def search_user_by_id(id):
    user_found = db.reference('users/' + id).get()
    return user_found


def enter_fingerprint(fingerprint, db):
    pending_user = validate_pending_user()

    if validate_connection() and pending_user:
        add_fingerprint(fingerprint, pending_user)
    else:
        if validate_connection():
            user_id = search_fingerprint_firebase(fingerprint)
        else:
            user_id = search_fingerprint_local(fingerprint, db)
        print('user id: ', user_id)

        if user_id:
            print('Opening door to {}'.format(user_id))
            if validate_connection():
                add_log_firebase(fingerprint, user_id)
            else:
                add_log_local(None, fingerprint, user_id, db)
            return 'OK'

        else:
            print('Blocking door')
            if validate_connection():
                add_log_firebase(fingerprint, None)
            else:
                add_log_local(None, fingerprint, None, db)
            return 'ERROR'


def validate_pending_user():
    return db.reference('users/').order_by_child('status').equal_to('PENDING').get()


def validate_connection():
    try:
        urllib2.urlopen('http://216.58.192.142', timeout=3)
        print('INTERNET OK')
        return True
    except urllib2.URLError as err:
        print('NO INTERNET')
        return False


client = MongoClient('localhost', 27017)
local_db = client['cda']

authenticate()
read_fingerprint = 'jdfjsdvbsdkvbsbvsbvsdbvs'

enter_fingerprint(read_fingerprint, local_db)
