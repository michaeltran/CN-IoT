#!/usr/bin/env python

# pylint: disable=C0111,C0301,C0325

import sys
import datetime
import socket
import select
import json
import struct
import threading
import time
import os
import customsqlserver

# INITIALIZATION
HOST = '172.31.20.21'
PORT = 5000
LONG_POLL = True
IMAGE_JSON_NAME = 'image.json'
DETAILS_JSON_NAME = 'details.json'
VERIFICATION_JSON_NAME = 'verify.json'
ADD_PERSON_JSON_NAME = 'add_person.json'
FPS_JSON_NAME = 'fps.json'
# SOCKET INITIALIZATION
CONNECTED_CLIENTS_SOCKETS = []
SERVER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER_SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
SERVER_SOCKET.bind((HOST, PORT))
SERVER_SOCKET.listen(10)
CONNECTED_CLIENTS_SOCKETS.append(SERVER_SOCKET)
print 'Serving Requests on: %s:%s' % (HOST, PORT)
# LOGGING INITIALIZATION
if not os.path.exists('Log'):
    os.makedirs('Log')
WRITE_LOG = True
REQUEST_LOG_PATH = 'Log/request.log'
if os.path.isfile(REQUEST_LOG_PATH):
    os.remove(REQUEST_LOG_PATH)
REQUEST_LOG_FILE = open(REQUEST_LOG_PATH, "w+")

def write_log(item, log_file, log_type):
    if WRITE_LOG:
        log_file.write("%s - %s: %d\n" % (datetime.datetime.now(), log_type, sys.getsizeof(item)))
# The following functions were taken from https://stackoverflow.com/questions/17667903/python-socket-receive-large-amount-of-data
def send_msg(sock, msg, log_file, log_type):
    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack('>I', len(msg)) + msg
    write_log(msg, log_file, log_type)
    sock.sendall(msg)
def recv_msg(sock, log_file, log_type):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4, log_file, '%s MESSAGE LENGTH' % (log_type))
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen, log_file, log_type)
def recvall(sock, n, log_file, log_type):
    # Helper function to recv n bytes or return None if EOF is hit
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        write_log(packet, log_file, log_type)
        data += packet
    return data

def background_thread_verification_function(sock):
    continue_flag = True
    while continue_flag:
        time.sleep(2)
        if os.path.isfile(VERIFICATION_JSON_NAME):
            with open(VERIFICATION_JSON_NAME, 'r') as the_file:
                send_msg(sock, the_file.read(), REQUEST_LOG_FILE, 'SEND AUTHORIZATION')
            os.remove(VERIFICATION_JSON_NAME)
            continue_flag = False

def background_thread_fps_function(sock):
    continue_flag = True
    while continue_flag:
        time.sleep(2)
        if os.path.isfile(FPS_JSON_NAME):
            with open(FPS_JSON_NAME, 'r') as the_file:
                send_msg(sock, the_file.read(), REQUEST_LOG_FILE, 'SEND FPS')
            os.remove(FPS_JSON_NAME)
            continue_flag = False

def background_thread_add_person_function(sock):
    continue_flag = True
    while continue_flag:
        time.sleep(2)
        if os.path.isfile(ADD_PERSON_JSON_NAME):
            with open(ADD_PERSON_JSON_NAME, 'r') as the_file:
                send_msg(sock, the_file.read(), REQUEST_LOG_FILE, 'SEND ADD_PERSON')
            os.remove(ADD_PERSON_JSON_NAME)
            continue_flag = False

def main(argv):
    while True:
        read_sockets, write_sockets, error_sockets = select.select(CONNECTED_CLIENTS_SOCKETS, [], [])
        for sock in read_sockets:
            if (sock == SERVER_SOCKET):
                sockfd, client_address = SERVER_SOCKET.accept()
                CONNECTED_CLIENTS_SOCKETS.append(sockfd)
            else:
                try:
                    data = recv_msg(sock, REQUEST_LOG_FILE, 'RECEIVE')
                    if data :
                        received_json = json.loads(data.strip())
                        print(str(datetime.datetime.now()), received_json['Type'])
                        #print('Serving: %s' % (received_json['Type']))
                        if (received_json['Type'] == 'PostImage'):
                            with open(IMAGE_JSON_NAME, 'w') as text_file:
                                text_file.write(json.dumps(received_json))
                            send_msg(sock, '', REQUEST_LOG_FILE, 'SEND IMAGE ACK')
                        elif (received_json['Type'] == 'PostDetails'):
                            if (received_json['ID'] != ''):
                                row = customsqlserver.get_face_data_sql(received_json['ID'])
                                if (row):
                                    received_json['ID'] = row.ID
                                    received_json['FirstName'] = row.FIRST_NAME
                                    received_json['LastName'] = row.LAST_NAME
                                    received_json['MinDistance'] = row.MIN_DISTANCE
                                    received_json['MaxDistance'] = row.MAX_DISTANCE
                            with open(DETAILS_JSON_NAME, 'w') as text_file:
                                text_file.write(json.dumps(received_json))
                        elif (received_json['Type'] == 'GetVerification'):
                            if LONG_POLL:
                                background_thread_verification = threading.Thread(target=background_thread_verification_function, args=(sock,))
                                background_thread_verification.start()
                            else:
                                if os.path.isfile(VERIFICATION_JSON_NAME):
                                    with open(VERIFICATION_JSON_NAME, 'r') as the_file:
                                        send_msg(sock, the_file.read(), REQUEST_LOG_FILE, 'SEND AUTHORIZATION')
                                    os.remove(VERIFICATION_JSON_NAME)
                                else:
                                    send_json = {}
                                    send_msg(sock, json.dumps(send_json), REQUEST_LOG_FILE, 'SEND NO AUTHORIZATION')
                        elif (received_json['Type'] == 'GetAddPerson'):
                            if LONG_POLL:
                                background_thread_add_person = threading.Thread(target=background_thread_add_person_function, args=(sock,))
                                background_thread_add_person.start()
                            else:
                                if os.path.isfile(ADD_PERSON_JSON_NAME):
                                    with open(ADD_PERSON_JSON_NAME, 'r') as the_file:
                                        send_msg(sock, the_file.read(), REQUEST_LOG_FILE, 'SEND ADD_PERSON')
                                    os.remove(ADD_PERSON_JSON_NAME)
                                else:
                                    send_json = {}
                                    send_msg(sock, json.dumps(send_json), REQUEST_LOG_FILE, 'SEND NO ADD_PERSON')
                        elif (received_json['Type'] == 'GetFPS'):
                            if LONG_POLL:
                                background_thread_fps = threading.Thread(target=background_thread_fps_function, args=(sock,))
                                background_thread_fps.start()
                            else:
                                if os.path.isfile(FPS_JSON_NAME):
                                    with open(FPS_JSON_NAME, 'r') as the_file:
                                        send_msg(sock, the_file.read(), REQUEST_LOG_FILE, 'SEND FPS')
                                    os.remove(FPS_JSON_NAME)
                                else:
                                    send_json = {}
                                    send_msg(sock, json.dumps(send_json), REQUEST_LOG_FILE, 'SEND NO FPS')
                        else:
                            print 'Unhandled input'
                            send_msg(sock, 'Unhandled input: %s' % received_json, REQUEST_LOG_FILE, 'SEND ERROR')
                except:
                    print "Unexpected error:", sys.exc_info()[0]
                    sock.close()
                    CONNECTED_CLIENTS_SOCKETS.remove(sock)
                    continue
    SERVER_SOCKET.close()

if __name__ == "__main__":
    main(sys.argv)