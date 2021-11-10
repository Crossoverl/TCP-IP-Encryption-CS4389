from threading import Thread    # Threading support
from cryptography.fernet import Fernet #symmetric encryption support
from cryptography.hazmat.primitives import hashes # provide hash support
from cryptography.hazmat.primitives.asymmetric import x25519 #key excahnge support
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import base64                   # For key derivation
import socket                   # Socket Programming support
import os

TARGET_ADDRESS = "0.0.0.0"      # Address of server we want to connect to
TARGET_PORT = 1234              # Port of the server we want to connect to
PRIV_KEY = X25519PrivateKey.generate() #X25519 Client Private Key
PUB_KEY = PRIV_KEY.public_key() # #X25519 Client Public Key
key = 0 # Symmentric Key
fernetObject = 0 # Fernet Class for symmentric encryption

server = socket.socket()                            # Create TCP socket
server.connect((TARGET_ADDRESS, TARGET_PORT))       # User created socket to connection to the target server
print("Connected to: ", TARGET_ADDRESS , " at port ", TARGET_PORT, "\nTo close connection, type: quit")

# Handle the listening for new messages from the server
def recvMessages():
    while True:
        global key
        global fernetObject
        incoming_message = server.recv(2048)        # Wait to receive upto 2 bytes of data from the server
        if key == 0:
            #Exchange Public Keys
            peer_pub_key = x25519.X25519PublicKey.from_public_bytes(incoming_message)
            server.send(
                PUB_KEY.public_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PublicFormat.Raw
                 )
            )
            shared_key = PRIV_KEY.exchange(peer_pub_key)

            #Derive Fernet Key
            salt = b"ThisIsForMatilda"
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            derived_key = kdf.derive(shared_key)
            key = base64.urlsafe_b64encode(derived_key)
            fernetObject = Fernet(key)

        else: 
            message = fernetObject.decrypt(incoming_message)
            message.decode()
            print("\n", str(message)[2:-1])

client_thread = Thread(target=recvMessages)         # Creation of the thread for new clients
client_thread.daemon = True
client_thread.start()

# Handle input of new messsages, and send new messages to the server
while True:
    new_message = input()
    if new_message.lower() == "quit":               # The user can close their own client by typing quit
        print("\nDisconnecting")
        break
    else:
        cipher = fernetObject.encrypt(new_message.encode())
        server.send(cipher)