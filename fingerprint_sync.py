import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from pymongo import MongoClient
import datetime
from os import system


def authenticate():
    cred = credentials.Certificate('google_credentiales.json')
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

    data = {'date': datetime.datetime.now()}
    local_db.syncs.insert_one(data)
    print('Change sync date')




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


client = MongoClient('localhost', 27017)
local_db = client['cda']


system('clear')
authenticate()
sync()
