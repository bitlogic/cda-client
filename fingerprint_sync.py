import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from pymongo import MongoClient
import datetime
from os import system, name

from delete_fingerprint import delete


def authenticate():
    cred = credentials.Certificate("google_credentials.json")
    firebase_admin.initialize_app(cred, options={
        'databaseURL': 'https://cda-bithouse.firebaseio.com/',
    })


def sync():
    check_inactive_users()

    # local_db.fingerprints.drop()
    # fingerprints = db.reference('fingerprints/').get()
    # for i in fingerprints:
    #     add_fingerprint(i, fingerprints[i]['user'])
    # print('Finish fingerprint sync')

    # local_db.users.drop()
    # users = db.reference('users/').get()
    # for i in users:
    #     add_user(i, users[i]['name'], users[i]['lastname'], users[i]['company'], users[i]['status'])
    # print('Finish user sync')

    # data = {'date': datetime.datetime.now()}
    # local_db.syncs.insert_one(data)
    # print('Change sync date')


def check_inactive_users():
   
    inactive_users = db.reference('users/').order_by_child('status').equal_to('INACTIVE').get():
    position_numbers = []
  
    for iu in inactive_users:
        user_fingerprints = db.reference('fingerprints/').order_by_child('user').equal_to(iu).get()
        if user_fingerprints: # Si no hay user_fingerprints --> Salir 
            continue
        else:
            return

        for fing in user_fingerprints:
            position_numbers.append(user_fingerprints[fing]['position_number'])
            
    position_numbers.sort()
   
    # Borra en el sensor
    for position_number in position_numbers:
        print(position_number)
        # if delete(position_number):
        #     print('Fingerprints deleted in sensor')

        # else:
        #     print('Error deleting fingerprints in sensor')

        # Borra en Firebase
        fingerprintdata = db.reference('fingerprints/').order_by_child('position_number').equal_to(position_number).get()
        print("Fingerprint data")
        print (fingerprintdata)
        for key in fingerprintdata:
            # db.reference('fingerprints/').child(key).delete()
            print("Key to delete")
            print(key)
    

        # Reduce de 1 todos los siguientes all position_numbers (todos, no solo los inactivos)
        next_fingerprints = db.reference('fingerprints/').order_by_child('position_number').start_at(position_number).get()
        for key, value in next_fingerprints.items():
            print("Key Value to shift back")
            print(key)
            print(value['position_number'])
            # db.reference('fingerprints/').child(key).update(
            #     {
            #         'position_number': value['position_number'] -1
            #     }
            # )

        check_inactive_users()

    


# def add_user(user_id, name, lastname, company, status):
#     data = {
#         '_id': user_id,
#         'name': name,
#         'lastname': lastname,
#         'status': status,
#         'company': company
#     }
#     local_db.users.insert_one(data)


# def add_fingerprint(fingerprint_id, user_id):
#     data = {
#         'fingerprint': fingerprint_id,
#         'user': user_id
#     }
#     local_db.fingerprints.insert_one(data)


# client = MongoClient('localhost', 27017)
# local_db = client['cda']
system('clear')
authenticate()
# sync()
inactive_users = db.reference('users/').order_by_child('status').equal_to('HOLA').get()
print(inactive_users)