from datetime import datetime

import firebase_admin
import pytz
from firebase_admin import credentials
from firebase_admin import db
import urllib.request as urllib2
from pymongo import MongoClient
import uuid
import os
import random
import string
import secrets



def search_fingerprint_firebase(fingerprint):
    print('Searching fingerprint in firebase')
    return db.reference('fingerprints/' + fingerprint).get()


def add_fingerprint(fingerprint, user):
    
    # Si la huella insertada no está en la base de datos THEN sigue con el proceso de carga de usuario
   
    if search_fingerprint_firebase(fingerprint) is None:
        fingerprints_list = []
        for x in range(0, 10):
            # Llama la función de lectura huella (mockeada en este caso con una random function secret.token
            next_fingerprint = secrets.token_hex(nbytes=16)
            fingerprints_list.append(next_fingerprint)
        
        
        fingerprint_ref = db.reference('fingerprints/')
        user_id = None
        for key, value in user.items():
            user_id = key
        print('Adding new fingerprint for ', user_id)  # Romi: TODO validar si la huella existe - Nico: se puede validar afuera de esta function, al principio de la enter_fingerprint
        
        for i in fingerprints_list:
            fingerprint_ref.child(i).set({
                'user': user_id
            })

  # Exception Handler en caso de perdida de conexion
  # Bulk import de huellas
  
    # Nico: Cambiar status de Pendiente a Active en Firebase si la huella se ha creado correctamente.
        users_ref = db.reference('users/')
        user_pending = users_ref.child(user_id)
        user_pending.update({'status':'ACTIVE' })
        print('Status changed to Active')


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

   
        if validate_connection():
            user_id = search_fingerprint_firebase(fingerprint)
        else:
            user_id = search_fingerprint_local(fingerprint, db)
        print('user id: ', user_id)

        if user_id:
            # En esta linea hay que llamar la function que abre la puerta. Luego se carga el log etc. Asi el usuario no se queda esperando mas tiempo en la puerta
            print('Opening door to {}'.format(user_id))
            if validate_connection():
                add_log_firebase(fingerprint, user_id)
            else:
                add_log_local(None, fingerprint, user_id, db)
            return 'OK'

        else:
            pending_user = validate_pending_user()
            user_id = search_fingerprint_firebase(fingerprint)

            if validate_connection() and pending_user and not user_id:
                add_fingerprint(fingerprint, pending_user)
                
            elif: pending_user is None:
                print('Blocking door')
                
                if validate_connection():
                    add_log_firebase(fingerprint, None)
                else:
                    add_log_local(None, fingerprint, None, db)
                return 'ERROR'
            
  
 

def validate_pending_user():
    if validate_connection ():
        return db.reference('users/').order_by_child('status').equal_to('PENDING').get()
    else:
        print('NO Internet - No se pudo validar usuario pendiente')    
        return False

def validate_connection():
    try:
        urllib2.urlopen('http://216.58.192.142', timeout=3)
        print('INTERNET OK')
        return True
    except urllib2.URLError as err:
        print('NO INTERNET')
        return False


client = MongoClient('localhost', 27020)
local_db = client['cda']

authenticate()
read_fingerprint = secrets.token_hex(nbytes=16)
search_fingerprint_local (read_fingerprint, local_db)
# enter_fingerprint(read_fingerprint, local_db)

