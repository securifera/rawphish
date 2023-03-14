##################################################################################
#  Description: Simple SMTP server for receiving email
#
#  Author: b0yd
#
#  Usage: Create MX record for domain pointing to FQDN of mail server
#         Create A record for FQDN of mail server to IP of server
#         python3 simple_smtp_server.py
##################################################################################

import quopri
from socket import *
import threading
import datetime

def handle_connection(client_socket):

    # Send a welcome message to the client
    client_socket.send(b'220 SMTP server\r\n')

    # Start an infinite loop to handle incoming commands from the client
    try:
        while True:
            # Receive a command from the client
            command = client_socket.recv(1024).decode('utf-8').strip()
            print("[*] Command: %s" % command)
            # Check if the client has disconnected
            if not command:
                break

            # Handle the client's command
            if command.startswith('EHLO') or command.startswith('HELO'):
                email_server = command.replace('EHLO:', '').strip()
                client_socket.send(b'250 Hello\r\n')
            elif command.startswith('MAIL FROM:'):
                email_from = command.replace('MAIL FROM:', '').strip()
                client_socket.send(b'250 OK\r\n')
            elif command.startswith('RCPT TO:'):
                email_to = command.replace('RCPT TO:', '').strip()
                client_socket.send(b'250 OK\r\n')
            elif command.startswith('DATA'):
                client_socket.send(b'354 End data with <CR><LF>.<CR><LF>\r\n')
                message = ''
                while True:
                    line = client_socket.recv(1024).decode('utf-8')
                    message += line
                    if message.endswith('\r\n.\r\n'):
                        break
                        
                # Decode the message
                message = quopri.decodestring(message)
                print(message)
                
                # Write message to a file
                if len(message) > 0:
                    now = datetime.datetime.now()
                    timestamp = now.strftime("%Y%m%d%H%M%S%f")
                    f = open(timestamp, 'wb')
                    f.write(message)
                    f.close()

                print("[*] Received data sending OK")
                client_socket.send(b'250 OK\r\n')
            elif command.startswith('QUIT'):
                client_socket.send(b'221 Bye\r\n')
                client_socket.close()
                break
            else:
                client_socket.send(b'500 Command not recognized\r\n')
    except Exception as e:
        print("[-] Exception: %s" % str(e))

    print("[*] Email received")

# Define the server and port to listen on
SERVER = '0.0.0.0'
PORT = 25

# Create a socket and bind it to the server and port
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind((SERVER, PORT))

# Set the server to listen for incoming connections
server_socket.listen(1)

print('SMTP server listening on port', PORT)

# Start an infinite loop to handle incoming connections
while True:
    # Wait for a client to connect
    client_socket, client_address = server_socket.accept()
    print('[*] Incoming connection from', client_address)

    threading.Thread(target=handle_connection, args=(client_socket,)).start()


# Close the server socket
server_socket.close()
