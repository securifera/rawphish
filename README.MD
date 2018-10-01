# Simple SMTP Script

usage: rawphish.py [-h] -d SERVERIP -r RECIPIENT -s SENDER [-p PLAIN_CONTENT]
                   [-m HTML_CONTENT] [-a ATTACHMENT] [-j SUBJECT] [-b BCC]
                   [-f FQDN] [--tls]

Send an email.

optional arguments:

    -h, --help        show this help message and exit
    -d SERVERIP       IP Address of the SMTP server.
    -r RECIPIENT      Email Recipient.
    -s SENDER         Email Sender.
    -p PLAIN_CONTENT  Path to file with plain text email content
    -m HTML_CONTENT   Path to file with HTML email content
    -a ATTACHMENT     Path to a file attachment
    -j SUBJECT        Email Subject
    -b BCC            Path to file with BCC Recipients
    -f FQDN           Fully qualified domain name of sending server
    --tls             Use TLS
