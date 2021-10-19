from threading import Thread    # Threading support
import socket                   # Socket Programming support
import select                   # Ascynchronous I/O with socket support

HOST_ADDRESS = "0.0.0.0"    # Servers address (0.0.0.0 for generic access)
HOST_PORT = 1234            # Servers port (Used in client scripts for connection to server)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      # TCP socket creation
server.bind((HOST_ADDRESS, HOST_PORT))                          # Bind the socket to our chosen address and port
server.listen(4)                                                # Listen for upto 4 connections
connected_clients = []                                          # Maintain list of currently connection clients
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
def removeClient(target_client):
    if target_client in connected_clients:
        connected_clients.remove(target_client)

#   Arguments: 
#       client_connection - The connection object for NEW client
#       client_address - Address / Port of NEWLY connected client
def intializeClient(client_connection, client_address):
    welcome_message = ("> Connected as " + str(client_address[1]))
    client_connection.send(welcome_message.encode())
    announcement_message = ("> User " + str(client_address[1]) + " connected")
    syncMessage(client_connection, announcement_message)

#   Arguments: 
#       connection - The connection object for client
#       connection_address - Address / Port of connected client
def clientConnection(connection, connection_address):
    intializeClient(connection, connection_address)
    while True:
        message = connection.recv(2048) # Accept and receive up to 2 bytes of data from the message
        if message:     # If messages contain content, send to other clients
            message.decode()
            formatted_message = ("[" + str(connection_address[1]) + "] : " + str(message)[2:-1])
            syncMessage(connection, formatted_message)
            print(formatted_message)
        else:           # If empty messages (disconnected) announce disconnect and disconnect user
            formatted_message = ("> User " + str(connection_address[1]) + " disconnected.")
            syncMessage(connection, formatted_message)
            print(str(connection_address) + " disconnected\nConnections: " + str((len(connected_clients) - 1)))
            removeClient(connection)
            break       # Kills thread

# Arguments:
#       connected_client - Client that send new message
#       message - Pure str of message send by connect_client
def syncMessage(connected_client, message):
    for client in connected_clients:
        if client == connected_client:      # Skip messaging client that sent original message
            continue
        else:
            try:        # Send every other client the message
                client.send(message.encode())
            except:     # The target client can't receive the message (maybe disconnected)
                client.close()
                removeClient(client) 

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





