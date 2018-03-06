#!/usr/bin/env python

# pylint: disable=C0111,C0301,C0325

import sys
import os
import socket
import json
import urlparse
import datetime
from shutil import copyfile
import customsqlserver

HOST = '172.31.20.21'
PORT = 5001
IMAGE_JSON_NAME = 'image.json'
VERIFICATION_JSON_NAME = 'verify.json'
ADD_PERSON_JSON_NAME = 'add_person.json'
FPS_JSON_NAME = 'fps.json'

SERVER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER_SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
SERVER_SOCKET.bind((HOST, PORT))
SERVER_SOCKET.listen(1)
print 'Serving HTTP Requests on: %s:%s' % (HOST, PORT)

# LOGGING INITIALIZATION
if not os.path.exists('Log'):
    os.makedirs('Log')
WRITE_LOG = True
HTTP_LOG_PATH = 'Log/http.log'
if os.path.isfile(HTTP_LOG_PATH):
    os.remove(HTTP_LOG_PATH)
HTTP_LOG_FILE = open(HTTP_LOG_PATH, "w+")

def write_log(item, log_file, log_type):
    if WRITE_LOG:
        log_file.write("%s - %s: %d\n" % (datetime.datetime.now(), log_type, sys.getsizeof(item)))

def main(argv):
    while True:
        connection, client_address = SERVER_SOCKET.accept()
        request = connection.recv(4096).decode('utf-8')
        write_log(request, HTTP_LOG_FILE, 'HTTP REQUEST')

        string_list = request.split(' ')     # Split request from spaces
        if (len(string_list) > 2):
            method = string_list[0]
            requesting_file = string_list[1]

            print(str(datetime.datetime.now()), 'Client request', requesting_file)

            # After the "?" symbol not relevent here
            myfile = requesting_file.split('?')[0]
            myfile = myfile.lstrip('/')

            parsed = urlparse.urlparse(requesting_file)
            parameters = urlparse.parse_qs(parsed.query)

            if(myfile == ''):
                myfile = 'index.html'    # Load index file as default

            try:
                if (method == 'GET'):
                    # Special Condition for JSON requests
                    if(myfile.endswith('.json')):
                        with open(myfile, 'rb') as image_file:
                            response = image_file.read()

                        header = 'HTTP/1.1 200 OK\n'
                        mimetype = 'application/json'
                        header += 'Content-Type: ' + str(mimetype) + '\n\n'
                    else:
                        with open(myfile, 'rb') as image_file:
                            response = image_file.read()

                        header = 'HTTP/1.1 200 OK\n'

                        if(myfile.endswith(".jpg")):
                            mimetype = 'image/jpg'
                        elif(myfile.endswith(".css")):
                            mimetype = 'text/css'
                        else:
                            mimetype = 'text/html'

                        header += 'Content-Type: ' + str(mimetype) + '\n\n'
                elif (method == 'POST'):
                    response = 'Message not Received Successfully'
                    if (myfile == 'Authenticate'):
                        if ('id' in parameters and 'firstname' in parameters and 'lastname' in parameters):
                            response = 'Message Received %s' % parameters['id'][0]
                            verification_json = {}
                            verification_json['ID'] = parameters['id'][0]
                            verification_json['FirstName'] = parameters['firstname'][0]
                            verification_json['LastName'] = parameters['lastname'][0]
                            with open(VERIFICATION_JSON_NAME, 'w') as text_file:
                                text_file.write(json.dumps(verification_json))
                        elif ('message' in parameters):
                            response = 'Message Received %s' % parameters['message'][0]
                            verification_json = {}
                            verification_json['Message'] = parameters['message'][0]
                            with open(VERIFICATION_JSON_NAME, 'w') as text_file:
                                text_file.write(json.dumps(verification_json))
                    elif (myfile == 'FPS'):
                        if ('fps' in parameters):
                            fps_json = {}
                            fps_json['FPS'] = parameters['fps'][0]
                            with open(FPS_JSON_NAME, 'w') as text_file:
                                text_file.write(json.dumps(fps_json))
                    elif (myfile == 'AddPerson'):
                        if ('firstname' in parameters and 'lastname' in parameters and 'mindistance' in parameters and 'maxdistance' in parameters):
                            with open(IMAGE_JSON_NAME, 'rb') as image_file:
                                resp = image_file.read()
                            data = json.loads(resp)
                            add_person_json = {}
                            add_person_json['Image'] = data['Image']
                            row = customsqlserver.add_person_sql(parameters['firstname'][0], parameters['lastname'][0], parameters['mindistance'][0], parameters['maxdistance'][0])
                            if row.ID:
                                add_person_json['ID'] = row.ID
                                with open(ADD_PERSON_JSON_NAME, 'w') as text_file:
                                    text_file.write(json.dumps(add_person_json))
                            response = 'Successfully Added'
                    header = 'HTTP/1.1 200 OK\n'
                    mimetype = 'application/json'
                    header += 'Content-Type: ' + str(mimetype) + '\n\n'

            except Exception as e:
                header = 'HTTP/1.1 404 Not Found\n\n'
                response = '<html><body><center><h3>Error 404: File not found</h3><p>Python HTTP Server</p></center></body></html>'.encode('utf-8')
                print '404 Not Found'
                print e

            final_response = header.encode('utf-8')
            final_response += response

            write_log(final_response, HTTP_LOG_FILE, 'HTTP SEND')

            connection.send(final_response)
            connection.close()

if __name__ == "__main__":
    main(sys.argv)