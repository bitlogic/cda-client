import time
import urllib.request as urllib2

import RPi.GPIO as GPIO
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from pymongo import MongoClient

from database_access import FirebaseAccess, MongoAccess
from fingerprint_reader import FingerprintReader

GPIO.setmode(GPIO.BCM) # GPIO Numbers instead of board numbers


def add_fingerprint(fingerprint, position_number, user):
    
    # Si la huella insertada no está en la base de datos THEN sigue con el proceso de carga de usuario

    fingerprints_list = [fingerprint]
    position_list = [position_number]

    reader.wait_fingerprint()
    next_fingerprint, next_position_number = reader.second_enroll()

    if next_fingerprint:
        fingerprints_list.append(next_fingerprint)
        position_list.append(next_position_number)

    fingerprint_ref = db.reference('fingerprints/')
    user_id = None
    for key, value in user.items():
        user_id = key
    print('Adding new fingerprint for ', user_id)

    for i, p in zip(fingerprints_list,position_list):
        fingerprint_ref.child(i).set({
            'user': user_id,
            'position_number': p
        })

    # Cambiar status de Pendiente a Active en Firebase si la huella se ha creado correctamente.
    users_ref = db.reference('users/')
    user_pending = users_ref.child(user_id)
    user_pending.update({'status':'ACTIVE' })
    print('Status changed to Active')


def authenticate():
    cred = credentials.Certificate("google_credentials.json")
    firebase_admin.initialize_app(cred, options={
        'databaseURL': 'https://cda-bithouse.firebaseio.com/',
    })


def enter_fingerprint(fingerprint):
    database = get_database_access()
    user_id = database.get_fingerprint(fingerprint)
    print('user id: ', user_id)

    if user_id:
        print('Opening door to {}'.format(user_id))
        open_door()

        database = get_database_access()
        database.add_log(fingerprint, user_id)

        return 'OK'

    else:
        return 'ERROR'


def open_door():
    relais_1_gpio = 17
    GPIO.setup(relais_1_gpio, GPIO.OUT)  # GPIO Assign mode
    GPIO.output(relais_1_gpio, GPIO.LOW)  # out
    time.sleep(5)
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
        return True
    except urllib2.URLError as err:
        return False


def read_fingerprint():
    reader.wait_fingerprint()

    fingerprint, _ =  reader.search_fingerprint()
       
    if fingerprint:
        return 1, fingerprint
    else:
        pending_user = validate_pending_user()
        if pending_user:
            new_fingerprint, new_position_number = reader.first_enroll()
            add_fingerprint(new_fingerprint, new_position_number, pending_user)
            return 2, new_fingerprint

    return 3, None
    

def execute():
    while True:
        try:
            status, fingerprint = read_fingerprint()
        except Exception as e:
            print(e)
            if e.args[0] == 'The received packet is corrupted (the checksum is wrong)!':
                print('Initializing the reader again')
                global reader
                reader = FingerprintReader()
            continue

        if status == 1:
            enter_fingerprint(fingerprint)
        elif status == 3:
            print('Blocking door')

            database = get_database_access()
            database.add_log(fingerprint, None)


def get_database_access():
   # if validate_connection():
      #  return firebase_access
   # else:
        return mongo_access


client = MongoClient('localhost', 27020)
local_db = client['cda']

authenticate()
reader = FingerprintReader()

firebase_access = FirebaseAccess(db)
mongo_access = MongoAccess(local_db)

execute()
