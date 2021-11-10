from threading import Thread    # Threading support
from cryptography.fernet import Fernet # symmetric encryption support
from cryptography.hazmat.primitives import hashes # provide hash support
from cryptography.hazmat.primitives.asymmetric import x25519 #key excahnge support
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import base64                   # for key derivation
import socket                   # Socket Programming support
import select                   # Ascynchronous I/O with socket support
import os

HOST_ADDRESS = "0.0.0.0"    # Servers address (0.0.0.0 for generic access)
HOST_PORT = 1234            # Servers port (Used in client scripts for connection to server)
PRIV_KEY = X25519PrivateKey.generate() # X25519 Server Private Key
PUB_KEY = PRIV_KEY.public_key() # X25519 Server Public Key

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      # TCP socket creation
server.bind((HOST_ADDRESS, HOST_PORT))                          # Bind the socket to our chosen address and port
server.listen(4)                                                # Listen for upto 4 connections
connected_clients = []                                          # Maintain list of currently connection clients
client_keys = []
print('''
    ███████╗███████╗██████╗ ██╗   ██╗███████╗██████╗ 
    ██╔════╝██╔════╝██╔══██╗██║   ██║██╔════╝██╔══██╗
    ███████╗█████╗  ██████╔╝██║   ██║█████╗  ██████╔╝
    ╚════██║██╔══╝  ██╔══██╗╚██╗ ██╔╝██╔══╝  ██╔══██╗
    ███████║███████╗██║  ██║ ╚████╔╝ ███████╗██║  ██║
    ╚══════╝╚══════╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝
                          RUNNING                                                                                                                                                   
''')
print("Listening on ", HOST_ADDRESS, " at port ", HOST_PORT, "\n")    

#   Arguments: 
#       target_client - The connection object for client to be removed
def removeClient(target_client, client_key):
    print(client_keys)
    if target_client in connected_clients:
        connected_clients.remove(target_client)
        client_keys.remove(client_key)
    print(client_keys)

#   Arguments: 
#       client_connection - The connection object for NEW client
#       client_address - Address / Port of NEWLY connected client
def intializeClient(client_connection, client_address):
    #Exchange Public Keys
    client_connection.send(
        PUB_KEY.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
    )
    peer_pub_key_bytes = client_connection.recv(2048)
    peer_pub_key = x25519.X25519PublicKey.from_public_bytes(peer_pub_key_bytes)
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

    #Finish Client Initialization
    announcement_message = ("> User " + str(client_address[1]) + " connected")
    syncMessage(client_connection, announcement_message)
    return key

#   Arguments: 
#       connection - The connection object for client
#       connection_address - Address / Port of connected client
def clientConnection(connection, connection_address):
    client_key = intializeClient(connection, connection_address)
    client_keys.append(client_key)
    client_fernet = Fernet(client_key)
    while True:
        cipher = connection.recv(2048) # Accept and receive up to 2 bytes of data from the message
        message = client_fernet.decrypt(cipher)
        if message:     # If messages contain content, send to other clients
            message.decode()
            formatted_message = ("[" + str(connection_address[1]) + "] : " + str(message)[2:-1])
            syncMessage(connection, formatted_message)
            print(formatted_message)
        else:           # If empty messages (disconnected) announce disconnect and disconnect user
            formatted_message = ("> User " + str(connection_address[1]) + " disconnected.")
            syncMessage(connection, formatted_message)
            print(str(connection_address) + " disconnected\nConnections: " + str((len(connected_clients) - 1)))
            removeClient(connection, client_key)
            break       # Kills thread

# Arguments:
#       connected_client - Client that send new message
#       message - Pure str of message send by connect_client
def syncMessage(connected_client, message):
    for x in range(len(connected_clients)):
        if connected_clients[x] == connected_client:      # Skip messaging client that sent original message
            continue
        else:
            try:        # Send every other client the message
                client_fernet = Fernet(client_keys[x])
                cipher = client_fernet.encrypt(message.encode())
                connected_clients[x].send(cipher)
            except:     # The target client can't receive the message (maybe disconnected)
                connected_clients[x].close()
                removeClient(connected_clients[x], client_keys[x]) 

while True:
    client_connection, client_addr = server.accept()                                        # Accept new connections
    connected_clients.append(client_connection)                                             # Add new connections to list of active connections
    print(str(client_addr) + " connected\nConnections: " + str(len(connected_clients)))     
    client_thread = Thread(target=clientConnection, args=(client_connection, client_addr))  # Start thread for new connections
    client_thread.daemon = True
    client_thread.start()

for clients in connected_clients:
    clients.close()

server.close()





