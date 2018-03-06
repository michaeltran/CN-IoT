#!/usr/bin/env python

import boto3
import uuid
import os

CLIENT = boto3.client('rekognition')

COLLECTION_ID = 'FaceCollection'
BUCKET_NAME = 'mtranbucket'

def add_person_opencv(decoded_img, external_image_id):
    # OpenCV
    if not os.path.exists('FaceDatabase/training-data/s%s' % (external_image_id)):
        os.makedirs('FaceDatabase/training-data/s%s' % (external_image_id))

    with open('FaceDatabase/training-data/s%s/%s.jpg' % (external_image_id, uuid.uuid4()),'wb') as f:
        f.write(decoded_img)

def add_person_aws(decoded_img, external_image_id):
    # AWS
    response = CLIENT.index_faces(
        CollectionId=COLLECTION_ID,
        DetectionAttributes=[],
        ExternalImageId=external_image_id,
        Image = { 'Bytes': decoded_img }
    )