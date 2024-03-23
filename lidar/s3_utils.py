import boto3
import os


def create_s3_client():
    return boto3.client('s3', region_name='nyc3', endpoint_url=os.environ.get('AWS_S3_ENDPOINT_URL'), aws_access_key_id=os.environ.get(
        'AWS_S3_ACCESS_KEY_ID'), aws_secret_access_key=os.environ.get('AWS_S3_SECRET_ACCESS_KEY'))


def generate_presigned_url_get(filepath):
    """
    Generate a presigned Amazon S3 URL that can be used to retrieve an object.
    """
    client = create_s3_client()
    bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    method = 'get_object'

    return client.generate_presigned_url(
        ClientMethod=method, Params={'Bucket': bucket, 'Key': f'media/lidar/lidar_scans/{filepath}'}, ExpiresIn=3600)


def generate_presigned_url_put(filepath):
    """
    Generate a presigned Amazon S3 URL that can be used to upload an object.
    """
    client = create_s3_client()
    bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    method = 'put_object'

    return client.generate_presigned_url(
        ClientMethod=method, Params={'Bucket': bucket, 'Key': f'media/lidar/lidar_scans/{filepath}'}, ExpiresIn=3600)


def get_object(filepath: str):
    client = create_s3_client()
    print('Got client')
    bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    print(f'{bucket = }')
    print(os.environ.get('AWS_S3_ACCESS_KEY_ID'))
    try:
        response = client.get_object(
            Bucket=bucket, Key=f'media/lidar/lidar_scans/{filepath}')
    except Exception as e:
        print(e)
        raise e
    print('Got response')
    obj = response['Body']
    print('Got body')
    return obj
