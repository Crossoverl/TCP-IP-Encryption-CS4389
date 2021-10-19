from threading import Thread    # Threading support
import socket                   # Socket Programming support

TARGET_ADDRESS = "0.0.0.0"      # Address of server we want to connect to
TARGET_PORT = 1234              # Port of the server we want to connect to

server = socket.socket()                            # Create TCP socket
server.connect((TARGET_ADDRESS, TARGET_PORT))       # User created socket to connection to the target server
print("Connected to: ", TARGET_ADDRESS , " at port ", TARGET_PORT, "\nTo close connection, type: quit")

# Handle the listening for new messages from the server
def recvMessages():
    while True:
        incoming_message = server.recv(2048)        # Wait to receive upto 2 bytes of data from the server
        incoming_message.decode()
        print("\n", str(incoming_message)[2:-1])

client_thread = Thread(target=recvMessages)         # Creation of the thread for new clients
client_thread.daemon = True
client_thread.start()

# Handle input of new messsages, and send new messages to the server
while True:
    new_message = input()
    if new_message.lower() == "quit":               # The user can close their own client by typing quit
        print("\nDisconnecting")
        break
    server.send(new_message.encode())