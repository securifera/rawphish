######################################################
# Description:    Simple SMTP script for sending email.
# Author:       b0yd@securifera
# License:      https://creativecommons.org/licenses/by/4.0/
# Example:      rawphish.py -d 64.233.177.27 -r johndoe@gmail.com -m body.txt 
#                  -s sender@phisher.com -j "Email Subject" -f phisher.com -a macro.xls
######################################################

import socket
import sys
import argparse
import base64
import random
import ssl
import os
import time
import email.utils
import quopri
import mimetypes

parser = argparse.ArgumentParser(description='Send an email.')
parser.add_argument('-d', dest='serverIp', help='IP Address of the SMTP server.', required=True)
parser.add_argument('-r', dest='recipient', help='Email Recipient.', required=True)
parser.add_argument('-s', dest='sender', help='Email Sender.', required=True)
parser.add_argument('-p', dest='plain_content', help='Path to file with plain text email content')
parser.add_argument('-m', dest='html_content', help='Path to file with HTML email content')
parser.add_argument('-a', dest='attachment', help='Path to a file attachment')
parser.add_argument('-j', dest='subject', help='Email Subject')
parser.add_argument('-b', dest='bcc', help='Path to file with BCC Recipients')
parser.add_argument('-f', dest='fqdn', help='Fully qualified domain name of sending server')
parser.add_argument('--tls', dest='use_tls', help='Use TLS', action='store_true')
parser.set_defaults(use_tls=False)

args = parser.parse_args()

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
    print('Failed to create socket')
    sys.exit()


port = 25
host = args.serverIp
try:
    remote_ip = socket.gethostbyname( host )
except socket.gaierror:
    #could not resolve
    print('Hostname could not be resolved. Exiting')
    sys.exit()

#Connect to remote server
s.connect((remote_ip , port))
print('Socket Connected to ' + host)

#Now receive data
reply = s.recv(4096).decode()
print(reply)

#Check if STARTTLS is supported
if args.use_tls:

    message = "EHLO " + args.fqdn + "\r\n"
    try :
        #Set the whole string
        s.sendall(message.encode())
    except socket.error:
        #Send failed
        print('Send failed')
        sys.exit()
    print(message + ': sent')

    #Now receive data
    reply = s.recv(4096).decode()
    print(reply)

    if "STARTTLS" in reply:
        message = "STARTTLS \r\n"
        try :
            #Set the whole string
            s.sendall(message.encode())
        except socket.error:
            #Send failed
            print('Send failed')
            sys.exit()
        print(message + ': sent')

        #Now receive data
        reply = s.recv(4096).decode()
        print(reply)

        #Wrap socket with TLS
        s = ssl.wrap_socket(s,cert_reqs=ssl.CERT_NONE,)

    else:
        print('[-] STARTTLS not supported. Exiting')
        sys.exit()

message = "HELO " + args.fqdn + "\r\n"
try :
    #Set the whole string
    s.sendall(message.encode())
except socket.error:
    #Send failed
    print('Send failed')
    sys.exit()

#Now receive data
reply = s.recv(4096).decode()
print(reply) 

#Send some data to remote server
message = "MAIL FROM: <" + args.sender + ">\r\n"
try :
    #Set the whole string
    s.sendall(message.encode())
except socket.error:
    #Send failed
    print('Send failed')
    sys.exit()
print('SENDER sent')

#Now receive data
reply = s.recv(4096).decode()
print(reply)

#Send some data to remote server
message = "RCPT TO: <" + args.recipient + ">\r\n"
try :
    #Set the whole string
    s.sendall(message.encode())
except socket.error:
    #Send failed
    print('Send failed')
    sys.exit()
print('RECEIVER sent')

#Now receive data
reply = s.recv(4096).decode()
print(reply)

if "rejected" in reply:
    print('[-] Recipient "'+ args.recipient +'" rejected. Exiting.')
    sys.exit()

#Send BCC recipients
if args.bcc:
    f = open(args.bcc, 'rb')
    bcc_lines = f.readlines()
    f.close()

    for bcc_rcpt in bcc_lines:
        rcpt = bcc_rcpt.strip().decode()

        #Send some data to remote server
        message = "RCPT TO: <" + rcpt + ">\r\n"
        try :
            #Set the whole string
            s.sendall(message.encode())
        except socket.error:
            #Send failed
            print('Send failed')
            sys.exit()

        #Now receive data
        reply = s.recv(4096).decode()
        print(reply)

        if "rejected" in reply:
            print('[-] Recipient "'+ rcpt +'" rejected. Exiting.')
            sys.exit()



#Send some data to remote server
message = "DATA\r\n"
try :
    #Set the whole string
    s.sendall(message.encode())
except socket.error:
    #Send failed
    print('Send failed')
    sys.exit()
print('DATA start sent')
 
#Now receive data
reply = s.recv(4096).decode()
print(reply)

msgId = str(random.randint( 1111111111, 9999999999 ))
outerId = '_000_' + msgId
innerMsgId = outerId

#Add the header
content_type = "alternative"
if args.attachment:
    content_type = "mixed"

message =  'Content-Type: multipart/'+ content_type + ';\r\n\tboundary="===============' + outerId + '=="\r\n'
message += 'MIME-Version: 1.0\r\n'
message += 'Subject: ' + args.subject + '\r\n'
message += 'Date: ' + email.utils.formatdate(time.time()) + '\r\n'
message += 'Message-ID: <' + msgId + "@" + args.fqdn + '>\r\n'
message += 'From: ' + args.sender + '\r\n'
message += 'To: ' + args.recipient + '\r\n\r\n'

#Add outer start boundary
message += '--===============' + outerId + '==\r\n'
if args.attachment:
    innerId = '_001_' + msgId
    message += 'Content-Type: multipart/related;\r\n\tboundary="===============' + innerId + '==";\r\n\t'
    message += 'type="multipart/alternative"\r\n\r\n'
    #Add boundary for msg
    innerMsgId = '_002_' + msgId
    message += '--===============' + innerId + '==\r\n'
    message += 'Content-Type: multipart/alternative;\r\n\tboundary="===============' + innerMsgId + '=="\r\n\r\n'


#Add plain text if specified
if args.plain_content:

    inner_body = ''
    with open(args.plain_content, 'rb') as f:
        inner_body = f.read()

        #Quote encode
        if len(inner_body):
            inner_body = quopri.encodestring(inner_body).decode()

    #Add inner msg boundary id
    if innerMsgId != outerId:
        message += '--===============' + innerMsgId + '==\r\n'

    #Add the plain message
    message += 'Content-Type: text/plain; charset="us-ascii"\r\n'
    message += 'Content-Transfer-Encoding: quoted-printable\r\n\r\n'
    message += inner_body + '\r\n\r\n'


#Read msg file
if args.html_content:

    inner_body = ''
    with open(args.html_content, 'rb') as f:
        inner_body = f.read()

        #Quote encode
        enc_body = quopri.encodestring(inner_body).decode()

    #Add inner msg boundary id
    if args.plain_content:
        message += '--===============' + innerMsgId + '==\r\n'

    #Add the HTML message
    message += 'Content-Type: text/html; charset="us-ascii"\r\n'
    message += 'Content-Transfer-Encoding: quoted-printable\r\n\r\n'
    message += enc_body + '\r\n\r\n'

if args.attachment :
    #Base64 encode the file
    file_str = ''
    with open(args.attachment, "rb") as f:
        file_str = f.read()

    # Convert from bytes to a base64-encoded ascii string
    bs = base64.encodestring(file_str)
    # Add it to the message
    file_name = args.attachment
    file_name = os.path.basename(file_name)

    #Add msg end boundary
    message += '--===============' + innerMsgId + '==--\r\n\r\n'

    #Add attachment start boundary
    mime_type = mimetypes.guess_type(file_name)
    message += '--===============' + innerId + '==\r\n'
    message += 'Content-Type: '+mime_type[0]+'\r\n'
    message += 'Content-ID: <'+file_name+'@' + args.fqdn + '>\r\n'
    message += 'Content-Disposition: attachment;\r\n\tfilename="' + file_name +'"\r\n'
    message += 'Content-Transfer-Encoding: base64\r\n\r\n'
    #Add base64 encoded file
    message += bs + '\r\n\r\n'
    message += '--===============' + innerId + '==--\r\n\r\n'

#Add outer end boundary
message += '--===============' + outerId + '==--\r\n'

#Add the message end flag
message += '.\r\n'

try :
    #Set the whole string
    s.sendall(message.encode())
except socket.error:
    #Send failed
    print('Send failed')
    sys.exit()
print('DATA sent')

#Now receive data
reply = s.recv(4096).decode()
print(reply)

#Send some data to remote server
message = "QUIT\r\n"
try :
    #Set the whole string
    s.sendall(message.encode())
except socket.error:
    #Send failed
    print('Send failed')
    sys.exit()
print('QUIT sent')

#Now receive data
reply = s.recv(4096).decode()
print(reply)


