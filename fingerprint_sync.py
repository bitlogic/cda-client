import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from pymongo import MongoClient


def authenticate():
    cred = credentials.Certificate("google_credentials.json")
    firebase_admin.initialize_app(cred, options={
        'databaseURL': 'https://cda-bithouse.firebaseio.com/',
    })


def sync():
    local_db.fingerprints.drop()
    fingerprints = db.reference('fingerprints/').get()
    for i in fingerprints:
        add_fingerprint(i, fingerprints[i]['user'])
    print('Finish fingerprint sync')

    local_db.users.drop()
    users = db.reference('users/').get()
    for i in users:
        add_user(i, users[i]['name'], users[i]['lastname'], users[i]['company'], users[i]['status'])
    print('Finish user sync')


def add_user(user_id, name, lastname, company, status):
    data = {
        '_id': user_id,
        'name': name,
        'lastname': lastname,
        'status': status,
        'company': company
    }
    local_db.users.insert_one(data)


def add_fingerprint(fingerprint_id, user_id):
    data = {
        'fingerprint': fingerprint_id,
        'user': user_id
    }
    local_db.fingerprints.insert_one(data)


client = MongoClient('localhost', 27020)
local_db = client['cda']

authenticate()
sync()
