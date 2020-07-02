import hashlib
from pyfingerprint.pyfingerprint import PyFingerprint
from pyfingerprint.pyfingerprint import FINGERPRINT_CHARBUFFER1


class FingerprintReader:

    def __init__(self):
        print('Creating fingerprint reader')

    def wait_for_fingerprint(self):
        ## Tries to initialize the sensor
        print('Fingerprint reader')
        try:
            f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

            if not f.verifyPassword():
                raise ValueError('The given fingerprint sensor password is wrong!')

        except Exception as e:
            print('The fingerprint sensor could not be initialized!')
            print('Exception message: ' + str(e))
            return None

        ## Gets some sensor information
        print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))

        ## Tries to search the finger and calculate hash
        try:
            print('Waiting for finger...')

            ## Wait that finger is read
            while not f.readImage():
                pass

            ## Converts read image to characteristics and stores it in charbuffer 1
            f.convertImage(FINGERPRINT_CHARBUFFER1)

            ## Searchs template
            result = f.searchTemplate()

            positionNumber = result[0]
            accuracyScore = result[1]

            if positionNumber == -1:
                print('No match found!')
                exit(0)
            else:
                print('Found template at position #' + str(positionNumber))
                print('The accuracy score is: ' + str(accuracyScore))

            ## OPTIONAL stuff
            ##

            ## Loads the found template to charbuffer 1
            f.loadTemplate(positionNumber, FINGERPRINT_CHARBUFFER1)

            ## Downloads the characteristics of template loaded in charbuffer 1
            characteristics = str(f.downloadCharacteristics(FINGERPRINT_CHARBUFFER1)).encode('utf-8')

            ## Hashes characteristics of template
            fingerprint_hash = hashlib.sha256(characteristics).hexdigest()
            print('SHA-2 hash of template: ' + fingerprint_hash)
            return fingerprint_hash


        except Exception as e:
            print('Operation failed!')
            print('Exception message: ' + str(e))
            return None