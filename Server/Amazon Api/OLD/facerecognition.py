import boto3
import json

sourceFileName= 'source.png'
targetFileName= 'source.png'
bucket = 'mtranbucket'
region = 'us-east-1'
client = boto3.client('rekognition',region)

response = client.detect_faces(
    Image={
        'S3Object': {
            'Bucket': bucket,
            'Name':targetFileName
        }
    },
    Attributes=['ALL']
)

print('Detected faces for ' + targetFileName)
for faceDetail in response['FaceDetails']:
    print('The detected face is between ' + str(faceDetail['AgeRange']['Low'])
            + ' and ' + str(faceDetail['AgeRange']['High']) + ' years old')
    print('Here are the other attributes:')
    print(json.dumps(faceDetail, indent=4, sort_keys=True))


