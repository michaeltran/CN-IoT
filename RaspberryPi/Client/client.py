#!/usr/bin/env python

import socket
import getopt
import sys
import datetime
import json
import base64
import struct
import os
import VL53L0X
import sched, time
import threading
import cv2
import boto3
import timeit
from contextlib import closing
import numpy
# Custom Python
global facerecognition
import facerecognition
import addperson

# Constants
HOST = '34.238.10.126'
PORT = 5000
# AWS Constants
#REGION = 'us-east-1'
#BUCKET_NAME = 'mtranbucket'
COLLECTION_ID = 'FaceCollection'
FACE_RECOGNITION_TYPE = 'AWS'

# Command-line Arguments
unixOptions = 'f:'
gnuOptions = ['face=']
fullCmdArguments = sys.argv
argumentList = fullCmdArguments[1:]
try:
    arguments, values = getopt.getopt(argumentList, unixOptions, gnuOptions)
except getopt.error as err:
    print (str(err))
    sys.exit(2)
for currentArgument, currentValue in arguments:
    if currentArgument in ('-f', '--face'):
        if currentValue == 'AWS' or currentValue == 'OPENCV':
            print('Using %s for face recognition.\n' % (currentValue))
            FACE_RECOGNITION_TYPE = currentValue

# AWS Initialization
s3 = boto3.client('s3')
client = boto3.client('rekognition')
polly = boto3.client('polly')
# CV2 Initialization
cam = cv2.VideoCapture(0)
def get_image():
    retval, im = cam.read()
    return im
# Distance Sensor Initialization
tof = VL53L0X.VL53L0X()
tof.start_ranging(VL53L0X.VL53L0X_BEST_ACCURACY_MODE)
# Socket Initialization
SERVER_ADDRESS = (HOST, PORT)
SOCK_MAIN = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SOCK_MAIN.connect(SERVER_ADDRESS)
SOCK_VERIFICATION = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SOCK_VERIFICATION.connect(SERVER_ADDRESS)
SOCK_DETAILS = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SOCK_DETAILS.connect(SERVER_ADDRESS)
SOCK_ADD_PERSON = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SOCK_ADD_PERSON.connect(SERVER_ADDRESS)
SOCK_FPS = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SOCK_FPS.connect(SERVER_ADDRESS)
# Scheduler Initialization
SCHEDULER_VERIFICATION = sched.scheduler(time.time, time.sleep)
SCHEDULER_DETAILS = sched.scheduler(time.time, time.sleep)
SCHEDULER_ADD_PERSON = sched.scheduler(time.time, time.sleep)
SCHEDULER_FPS = sched.scheduler(time.time, time.sleep)
# Threading Variables
c = threading.Condition()
global GLOBAL_IMAGE
global GLOBAL_EXIT_FLAG
GLOBAL_IMAGE = ''
GLOBAL_EXIT_FLAG = False
# Logging Variables
if not os.path.exists('Log'):
    os.makedirs('Log')
WRITE_LOG = True
IMAGE_LOG_PATH = 'Log/image.log'
DETAILS_LOG_PATH = 'Log/details.log'
AUTHORIZATION_LOG_PATH = 'Log/authorization.log'
FACE_RECOGNITION_LOG_PATH = 'Log/facerecognition.log'
ADD_PERSON_LOG_PATH = 'Log/add_person.log'
FPS_LOG_PATH = 'Log/fps.log'
if os.path.isfile(IMAGE_LOG_PATH):
    os.remove(IMAGE_LOG_PATH)
if os.path.isfile(DETAILS_LOG_PATH):
    os.remove(DETAILS_LOG_PATH)
if os.path.isfile(AUTHORIZATION_LOG_PATH):
    os.remove(AUTHORIZATION_LOG_PATH)
if os.path.isfile(FACE_RECOGNITION_LOG_PATH):
    os.remove(FACE_RECOGNITION_LOG_PATH)
if os.path.isfile(ADD_PERSON_LOG_PATH):
    os.remove(ADD_PERSON_LOG_PATH)
if os.path.isfile(FPS_LOG_PATH):
    os.remove(FPS_LOG_PATH)
IMAGE_LOG_FILE = open(IMAGE_LOG_PATH, "w+")
DETAILS_LOG_FILE = open(DETAILS_LOG_PATH, "w+")
AUTHORIZATION_LOG_FILE = open(AUTHORIZATION_LOG_PATH, "w+")
FACE_RECOGNITION_LOG_FILE = open(FACE_RECOGNITION_LOG_PATH, "w+")
ADD_PERSON_LOG_FILE = open(ADD_PERSON_LOG_PATH, "w+")
FPS_LOG_FILE = open(FPS_LOG_PATH, "w+")

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
    #write_log(raw_msglen, log_file, log_type)
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


def get_face_data(decoded_image):
    if (FACE_RECOGNITION_TYPE == 'AWS'):
        return get_face_data_aws(decoded_image)
    elif (FACE_RECOGNITION_TYPE == 'OPENCV'):
        return get_face_data_opencv(decoded_image)

def get_face_data_aws(decoded_image):
    face_data_json = {}
    face_data_json['ID'] = ''
    face_data_json['FirstName'] = ''
    face_data_json['LastName'] = ''

    write_log(decoded_image, FACE_RECOGNITION_LOG_FILE, 'REKOGNITION DETECT_FACES IMAGE')
    response = client.detect_faces(
        Image = { 'Bytes': decoded_image }
    )
    if (response['FaceDetails']) :
        write_log(COLLECTION_ID, FACE_RECOGNITION_LOG_FILE, 'REKOGNITION SEARCH_FACES_BY_IMAGE COLLECTIONID')
        write_log(decoded_image, FACE_RECOGNITION_LOG_FILE, 'REKOGNITION SEARCH_FACES_BY_IMAGE IMAGE')
        response = client.search_faces_by_image(
            CollectionId = COLLECTION_ID,
            Image = { 'Bytes': decoded_image }
        )
        if (response['FaceMatches']) :
            #print response['FaceMatches']
            face_data_json['ID'] = response['FaceMatches'][0]['Face']['ExternalImageId']
            print(response['FaceMatches'][0]['Face']['ExternalImageId'], response['FaceMatches'][0]['Face']['Confidence'])
            #print 'Detected: %s %s' % (row.FIRST_NAME, row.LAST_NAME)
    write_log(decoded_image, FACE_RECOGNITION_LOG_FILE, 'REKOGNITION DETECT_FACES END')
    return face_data_json

def get_face_data_opencv(decoded_image):
    face_data_json = {}
    face_data_json['ID'] = ''
    face_data_json['FirstName'] = ''
    face_data_json['LastName'] = ''

    write_log(decoded_image, FACE_RECOGNITION_LOG_FILE, 'OPENCV DETECT_FACES START')
    label, confidence = facerecognition.predict(decoded_image)
    print(label, confidence)
    write_log(decoded_image, FACE_RECOGNITION_LOG_FILE, 'OPENCV DETECT_FACES END')
    if (label and confidence > 10):
        face_data_json['ID'] = label

    return face_data_json

def scheduled_fps_function(args):
    global GLOBAL_EXIT_FLAG
    global GLOBAL_REFRESH_RATE
    try:
        send_json = {}
        send_json['Type'] = 'GetFPS'
        send_msg(SOCK_FPS, json.dumps(send_json), FPS_LOG_FILE, 'GET FPS')
        data = recv_msg(SOCK_FPS, FPS_LOG_FILE, 'RECEIVE FPS')
        if data:
            data_json = json.loads(data)
            if data_json:
                print('Setting FPS to: %s' % (data_json['FPS']))
                GLOBAL_REFRESH_RATE = 1.0/int(data_json['FPS'])
    except Exception as e:
        print('scheduled_fps_function')
        print e
    finally:
        pass

    if not GLOBAL_EXIT_FLAG:
        SCHEDULER_FPS.enter(2, 1, scheduled_fps_function, ('',))
    else:
        SOCK_FPS.close()

def background_thread_fps_function():
    SCHEDULER_FPS.enter(5, 1, scheduled_fps_function, ('',))
    SCHEDULER_FPS.run()

background_thread_fps = threading.Thread(target=background_thread_fps_function, args=[])
background_thread_fps.start()

def scheduled_add_person_function(args):
    global GLOBAL_EXIT_FLAG
    global facerecognition
    try:
        send_json = {}
        send_json['Type'] = 'GetAddPerson'
        send_msg(SOCK_ADD_PERSON, json.dumps(send_json), AUTHORIZATION_LOG_FILE, 'GET ADD_PERSON')
        data = recv_msg(SOCK_ADD_PERSON, AUTHORIZATION_LOG_FILE, 'RECEIVE ADD_PERSON')
        if data:
            data_json = json.loads(data)
            if data_json:
                print('Adding Person: %s' % (str(data_json['ID'])))
                addperson.add_person_aws(base64.b64decode(data_json['Image']), str(data_json['ID']))
                addperson.add_person_opencv(base64.b64decode(data_json['Image']), str(data_json['ID']))
                facerecognition.prepare_data()
    except Exception as e:
        print('scheduled_add_person_function')
        print e
    finally:
        pass

    if not GLOBAL_EXIT_FLAG:
        SCHEDULER_ADD_PERSON.enter(2, 1, scheduled_add_person_function, ('',))
    else:
        SOCK_ADD_PERSON.close()

def background_thread_add_person_function():
    SCHEDULER_ADD_PERSON.enter(5, 1, scheduled_add_person_function, ('',))
    SCHEDULER_ADD_PERSON.run()

background_thread_add_person = threading.Thread(target=background_thread_add_person_function, args=[])
background_thread_add_person.start()

def scheduled_verification_function(args):
    global GLOBAL_EXIT_FLAG
    try:
        send_json = {}
        send_json['Type'] = 'GetVerification'
        send_msg(SOCK_VERIFICATION, json.dumps(send_json), AUTHORIZATION_LOG_FILE, 'GET AUTHORIZATION')
        data = recv_msg(SOCK_VERIFICATION, AUTHORIZATION_LOG_FILE, 'RECEIVE AUTHORIZATION')
        if data:
            data_json = json.loads(data)
            if data_json:
                response = polly.synthesize_speech(Text=data_json['Message'], OutputFormat='mp3', VoiceId='Salli')
                with closing(response["AudioStream"]) as stream:
                    with open('audio.mp3', 'wb') as file:
                        file.write(stream.read())
                os.system('mpg123 -q audio.mp3')
    except Exception as e:
        print('scheduled_verification_function')
        print e
    finally:
        pass

    if not GLOBAL_EXIT_FLAG:
        SCHEDULER_VERIFICATION.enter(2, 1, scheduled_verification_function, ('',))
    else:
        SOCK_VERIFICATION.close()

def background_thread_verification_function():
    SCHEDULER_VERIFICATION.enter(2, 1, scheduled_verification_function, ('',))
    SCHEDULER_VERIFICATION.run()

background_thread_verification = threading.Thread(target=background_thread_verification_function, args=[])
background_thread_verification.start()

def scheduled_details_function(args):
    global GLOBAL_IMAGE
    global GLOBAL_EXIT_FLAG
    send_json = {}
    try:
        if GLOBAL_IMAGE:
            send_json = get_face_data(GLOBAL_IMAGE)
            send_json['Type'] = 'PostDetails'
            send_json['Distance'] = tof.get_distance()
            send_msg(SOCK_DETAILS, json.dumps(send_json), DETAILS_LOG_FILE, 'SEND DETAILS')
    except Exception as e:
        print('scheduled_details_function')
        print e
    finally:
        pass

    if not GLOBAL_EXIT_FLAG:
        SCHEDULER_DETAILS.enter(5, 1, scheduled_details_function, ('',))
    else:
        SOCK_DETAILS.close()

def background_thread_details_function():
    SCHEDULER_DETAILS.enter(5, 1, scheduled_details_function, ('',))
    SCHEDULER_DETAILS.run()

background_thread_details = threading.Thread(target=background_thread_details_function, args=[])
background_thread_details.start()

global GLOBAL_REFRESH_RATE 
GLOBAL_REFRESH_RATE = 1.0/5.0
MIN_RESCALE = 0.1
MAX_RESCALE = 0.5
RESCALE_STEP = 0.02
CURRENT_RESCALE_FACTOR = MAX_RESCALE

ELAPSED_LENGTH = 5
PAST_ELAPSED_TOTAL_ARRAY = [0] * ELAPSED_LENGTH
ITERATOR = 0

def determine_rescale_factor(t_current_rescale_factor, t_past_elapsed_total_array, t_refresh_rate):
    average_elapsed_time = numpy.sum(t_past_elapsed_total_array)/ELAPSED_LENGTH
    if (average_elapsed_time > t_refresh_rate):
        if (t_current_rescale_factor > MIN_RESCALE):
            t_current_rescale_factor -= RESCALE_STEP
    elif (average_elapsed_time < t_refresh_rate):
        if (t_current_rescale_factor < MAX_RESCALE):
            t_current_rescale_factor += RESCALE_STEP
    return t_current_rescale_factor

try:
    while True:
        start_time = timeit.default_timer()
        camera_capture = get_image()
        camera_capture_resize = cv2.resize(camera_capture, (0,0), fx=CURRENT_RESCALE_FACTOR, fy=CURRENT_RESCALE_FACTOR)
        elapsed_camera_get_time = timeit.default_timer() - start_time
        GLOBAL_IMAGE = cv2.imencode('.jpg', camera_capture)[1].tostring()

        #cv2.imwrite('temp.jpg', camera_capture)
        encoded_string = base64.b64encode(cv2.imencode('.jpg', camera_capture_resize)[1].tostring())

        send_json = {}
        send_json['Type'] = 'PostImage'
        send_json['Image'] = encoded_string

        elapsed_time_processing = timeit.default_timer() - start_time

        start_time = timeit.default_timer()

        send_msg(SOCK_MAIN, json.dumps(send_json), IMAGE_LOG_FILE, 'SEND IMAGE')
        data = recv_msg(SOCK_MAIN, IMAGE_LOG_FILE, 'GET IMAGE RESPONSE')

        elapsed_sending = timeit.default_timer() - start_time

        elapsed_total = elapsed_time_processing + elapsed_sending
        datarate = sys.getsizeof(json.dumps(send_json))/elapsed_total

        #print('Elapsed Time Camera: ', elapsed_camera_get_time)
        #print('Elapsed Time Processing: ', elapsed_time_processing)
        #print('Elapsed Time Sending: ', elapsed_sending)
        #print('Total Elapsed: ', elapsed_total)
        #print('Data Rate: ', datarate)
        #print('')

        PAST_ELAPSED_TOTAL_ARRAY[ITERATOR] = elapsed_total

        PAST_DATA_RATE = datarate
        CURRENT_RESCALE_FACTOR = determine_rescale_factor(CURRENT_RESCALE_FACTOR, PAST_ELAPSED_TOTAL_ARRAY, GLOBAL_REFRESH_RATE)

        ITERATOR = (ITERATOR + 1) % ELAPSED_LENGTH
finally:
    GLOBAL_EXIT_FLAG = True
    SOCK_MAIN.close()
    del(cam)