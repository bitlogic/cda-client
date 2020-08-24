import urllib.request as urllib2
import uuid
from datetime import datetime

import pytz
from firebase_admin import credentials
from firebase_admin import db
import firebase_admin
from pymongo import MongoClient
from fingerprint_reader import FingerprintReader

import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM) # GPIO Numbers instead of board numbers


def search_fingerprint_firebase(fingerprint):
    print('Searching fingerprint in firebase')
    return db.reference('fingerprints/' + fingerprint).get()


def add_fingerprint(fingerprint, user):
    
    # Si la huella insertada no está en la base de datos THEN sigue con el proceso de carga de usuario

    fingerprints_list = [fingerprint]
    reader.wait_fingerprint()
    next_fingerprint = reader.enroll_fingerprint()

    if next_fingerprint:
        fingerprints_list.append(next_fingerprint)

    fingerprint_ref = db.reference('fingerprints/')
    user_id = None
    for key, value in user.items():
        user_id = key
    print('Adding new fingerprint for ', user_id)

    for i in fingerprints_list:
        fingerprint_ref.child(i).set({
            'user': user_id
        })

    # Cambiar status de Pendiente a Active en Firebase si la huella se ha creado correctamente.
    users_ref = db.reference('users/')
    user_pending = users_ref.child(user_id)
    user_pending.update({'status':'ACTIVE' })
    print('Status changed to Active')


def search_fingerprint_local(fingerprint):
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


def add_log_local(user, hash, user_id):
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


def enter_fingerprint(fingerprint):
    if validate_connection():
        user_id = search_fingerprint_firebase(fingerprint)
    else:
        user_id = search_fingerprint_local(fingerprint)
    print('user id: ', user_id)

    if user_id:
        print('Opening door to {}'.format(user_id))
        open_door()

        if validate_connection():
            add_log_firebase(fingerprint, user_id)
        else:
            add_log_local(None, fingerprint, user_id)
        return 'OK'

    else:
        pending_user = validate_pending_user()

        if validate_connection() and pending_user:
            add_fingerprint(fingerprint, pending_user)
            return 'OK - Usuario agregado en Firebase'
        else:
            return 'ERROR'


def open_door():
    relais_1_gpio = 17
    GPIO.setup(relais_1_gpio, GPIO.OUT)  # GPIO Assign mode
    GPIO.output(relais_1_gpio, GPIO.LOW)  # out
    time.sleep(1)
    GPIO.output(relais_1_gpio, GPIO.HIGH)  # on ñ.


def validate_pending_user():
    if validate_connection():
        return db.reference('users/').order_by_child('status').equal_to('PENDING').get()
    else:
        print('NO Internet - No se pudo validar usuario pendiente')
        return None


def validate_connection():
    try:
        urllib2.urlopen('http://216.58.192.142', timeout=3)
        print('INTERNET OK')
        return True
    except urllib2.URLError as err:
        print('NO INTERNET')
        return False


def read_fingerprint():
    reader.wait_fingerprint()

    pending_user = validate_pending_user()

    if pending_user:
        return reader.enroll_fingerprint()
    else:
        return reader.search_fingerprint()


def execute():
    while True:
        fingerprint = read_fingerprint()

        if fingerprint:
            enter_fingerprint(fingerprint)
        else:
            print('Blocking door')

            if validate_connection():
                add_log_firebase(fingerprint, None)
            else:
                add_log_local(None, fingerprint, None)
            return 'ERROR'


client = MongoClient('localhost', 27020)
local_db = client['cda']

authenticate()
reader = FingerprintReader()

execute()
