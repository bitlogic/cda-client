import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from os import system, getenv
from delete_fingerprint import delete


def authenticate():
    g_cred = getenv('CREDENTIALS') if getenv('CREDENTIALS') else 'google_credentiales.json'
    cred = credentials.Certificate(g_cred)
    firebase_admin.initialize_app(cred, options={
        'databaseURL': 'https://cda-bithouse.firebaseio.com/',
    })
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
            
system('clear')
authenticate()
delete_inactive_fingerprints()
delete_inactive_users()
