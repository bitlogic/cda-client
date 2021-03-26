import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import datetime
from os import system
from tinydb import TinyDB


def authenticate():
    cred = credentials.Certificate('/home/pi/Documents/cda-client/google_credentiales.json')
    firebase_admin.initialize_app(cred, options={
        'databaseURL': 'https://cda-bithouse.firebaseio.com/',
    })


def sync():

    local_db.table('fingerprints').truncate()
    fingerprints = db.reference('fingerprints/').get()
    for i in fingerprints:
        add_fingerprint(i, fingerprints[i]['user'])
    print('Finish fingerprint sync')

    local_db.table('users').truncate()
    users = db.reference('users/').get()
    for i in users:
        add_user(i, users[i]['name'], users[i]['lastname'], users[i]['company'], users[i]['status'])
    print('Finish user sync')

    data = {'date': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}
    local_db.table('syncs').insert(data)
    print('Change sync date')




def add_user(user_id, name, lastname, company, status):
    data = {
        '_id': user_id,
        'name': name,
        'lastname': lastname,
        'status': status,
        'company': company
    }
    local_db.table('users').insert(data)


def add_fingerprint(fingerprint_id, user_id):
    data = {
        'fingerprint': fingerprint_id,
        'user': user_id
    }
    local_db.table('fingerprints').insert(data)


local_db = TinyDB('./cda.json')


system('clear')
authenticate()
sync()
