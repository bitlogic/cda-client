import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from pymongo import MongoClient
import datetime
from os import system, name
from delete_fingerprint import delete
import psutil


def kill_access_controller():
    processname = "python3"

    for proc in psutil.process_iter():
        # check whether the process name matches
        if proc.name() == processname:
            proc.kill()


def authenticate():
    cred = credentials.Certificate("google_credentials.json")
    firebase_admin.initialize_app(cred, options={
        'databaseURL': 'https://cda-bithouse.firebaseio.com/',
    })


# def sync():
    
    

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


def delete_inactive_fingerprints():
    
    
    inactive_users = db.reference('users/').order_by_child('status').equal_to('INACTIVE').get()
    position_numbers = []
  
    for iu in inactive_users:
        user_fingerprints = db.reference('fingerprints/').order_by_child('user').equal_to(iu).get()

        for fing in user_fingerprints:
            position_numbers.append(user_fingerprints[fing]['position_number'])
    
    position_numbers.sort()
   
    for position_number in position_numbers:

       
        print(position_number)

         # Borra en el sensor


        if delete(position_number):
            print('Fingerprints deleted in sensor')

        else:
            print('Error deleting fingerprints in sensor')
            return

        # Borra en Firebase
        
        fingerprintdata = db.reference('fingerprints/').order_by_child('position_number').equal_to(position_number).get()
        for key in fingerprintdata:
            db.reference('fingerprints/').child(key).delete()
         

        # Reduce de 1 todos los siguientes all position_numbers (todos, no solo los inactivos)

        # next_fingerprints = db.reference('fingerprints/').order_by_child('position_number').start_at(position_number).get()
        # for key, value in next_fingerprints.items():
           
        #     db.reference('fingerprints/').child(key).update(
        #         {
        #             'position_number': value['position_number'] -1
        #         }
        #     )
        # # Reduce los position_numbers de -1
        
        # position_numbers = [x - 1 for x in position_numbers]
    

def delete_inactive_users():

    inactive_users = db.reference('users/').order_by_child('status').equal_to('INACTIVE').get()
    for key in inactive_users:
            db.reference('users/').child(key).delete()




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

kill_access_controller()
system('clear')
authenticate()
# sync()
delete_inactive_fingerprints()
delete_inactive_users()
print("Killed")