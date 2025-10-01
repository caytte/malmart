import nfc
import binascii

def connected(tag):
    idm = binascii.hexlify(tag.idm)
    print(idm)
    return False

clf = nfc.ContactlessFrontend('usb')
clf.connect(rdwr={'on-connect': connected})
clf.close()