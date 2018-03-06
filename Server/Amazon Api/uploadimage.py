import boto3

region = 'us-east-1'

s3 = boto3.client('s3')
client = boto3.client('rekognition',region)

collection_id='FaceCollection'
michaelfile1='michael1.jpg'
michaelfile2='michael2.png'
michaelfile3='michael3.jpg'
suefile1='sue1.png'
bambifile1='bambi1.jpg'
gloriafile1='gloria1.jpg'
dawnfile1='dawn1.jpg'
dawnfile2='dawn2.jpg'
dawnfile3='dawn3.jpg'
bucket_name='mtranbucket'

#delete/create collections
try:
    client.delete_collection(CollectionId=collection_id)
except:
    print 'Could not delete'

client.create_collection(CollectionId=collection_id)
#upload the images to s3
s3.upload_file(michaelfile1, bucket_name, michaelfile1)
s3.upload_file(michaelfile2, bucket_name, michaelfile2)
s3.upload_file(michaelfile3, bucket_name, michaelfile3)
s3.upload_file(suefile1, bucket_name, suefile1)
s3.upload_file(bambifile1, bucket_name, bambifile1)
s3.upload_file(gloriafile1, bucket_name, gloriafile1)
s3.upload_file(dawnfile1, bucket_name, dawnfile1)
s3.upload_file(dawnfile2, bucket_name, dawnfile2)
s3.upload_file(dawnfile3, bucket_name, dawnfile3)

#add images to face rekognition collection
response = client.index_faces(
    CollectionId=collection_id,
    DetectionAttributes=[],
    ExternalImageId='1',
    Image={
        'S3Object': {
            'Bucket':bucket_name,
            'Name':michaelfile1
            }
        }
    )
response = client.index_faces(
    CollectionId=collection_id,
    DetectionAttributes=[],
    ExternalImageId='1',
    Image={
        'S3Object': {
            'Bucket':bucket_name,
            'Name':michaelfile2
            }
        }
    )

response = client.index_faces(
    CollectionId=collection_id,
    DetectionAttributes=[],
    ExternalImageId='1',
    Image={
        'S3Object': {
            'Bucket':bucket_name,
            'Name':michaelfile3
            }
        }
    )

response = client.index_faces(
    CollectionId=collection_id,
    DetectionAttributes=[],
    ExternalImageId='2',
    Image={
        'S3Object': {
            'Bucket':bucket_name,
            'Name':suefile1
            }
        }
    )

response = client.index_faces(
    CollectionId=collection_id,
    DetectionAttributes=[],
    ExternalImageId='3',
    Image={
        'S3Object': {
            'Bucket':bucket_name,
            'Name':bambifile1
            }
        }
    )

response = client.index_faces(
    CollectionId=collection_id,
    DetectionAttributes=[],
    ExternalImageId='4',
    Image={
        'S3Object': {
            'Bucket':bucket_name,
            'Name':gloriafile1
            }
        }
    )

response = client.index_faces(
    CollectionId=collection_id,
    DetectionAttributes=[],
    ExternalImageId='5',
    Image={
        'S3Object': {
            'Bucket':bucket_name,
            'Name':dawnfile1
            }
        }
    )

response = client.index_faces(
    CollectionId=collection_id,
    DetectionAttributes=[],
    ExternalImageId='5',
    Image={
        'S3Object': {
            'Bucket':bucket_name,
            'Name':dawnfile2
            }
        }
    )

response = client.index_faces(
    CollectionId=collection_id,
    DetectionAttributes=[],
    ExternalImageId='5',
    Image={
        'S3Object': {
            'Bucket':bucket_name,
            'Name':dawnfile3
            }
        }
    )

response = client.search_faces_by_image(
    CollectionId=collection_id,
    Image={
        'S3Object': {
            'Bucket':bucket_name,
            'Name':dawnfile2
            }
        }
    )
print response
