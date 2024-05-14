import boto3
import os


def create_s3_client():
    return boto3.client('s3', region_name='nyc3', endpoint_url=os.environ.get('AWS_S3_ENDPOINT_URL'), aws_access_key_id=os.environ.get(
        'AWS_S3_ACCESS_KEY_ID'), aws_secret_access_key=os.environ.get('AWS_S3_SECRET_ACCESS_KEY'))


def generate_presigned_url_get(filepath):
    """
    Generate a presigned Amazon S3 URL that can be used to retrieve an object.

    Args:
        filepath (str): location of the object inside the folder 'media/lidar/lidar_scans' which is
        located in the Digital Ocean Spaces S3 bucket. In practice, this should be the name of the object
        i.e. 'kia_seltos_2022.glb'
    Returns:
        str: the url that is the location of the object inside the Digital Ocean Spaces S3 bucket
    """
    client = create_s3_client()
    bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    method = 'get_object'

    return client.generate_presigned_url(
        ClientMethod=method, Params={'Bucket': bucket, 'Key': f'media/lidar/lidar_scans/{filepath}'}, ExpiresIn=3600)


def generate_presigned_url_put(filepath):
    """
    Generate a presigned Amazon S3 URL that can be used to upload an object.

    Args:
        filepath (str): intended location of the object inside the folder 'media/lidar/lidar_scans' which is
        located in the Digital Ocean Spaces S3 bucket. In practice, this should be the name of the object
        i.e. 'kia_seltos_2022.glb'
    Returns:
        str: the url that can be used to upload an object to the Digital Ocean Spaces S3 bucket
    """
    client = create_s3_client()
    bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    method = 'put_object'

    return client.generate_presigned_url(
        ClientMethod=method, Params={'Bucket': bucket, 'Key': f'media/lidar/lidar_scans/{filepath}'}, ExpiresIn=3600)


def get_object(filepath: str):
    """
    Grab the binary data of a media file in the Digital Ocean Spaces S3 bucket

    Args:
        filepath (str): location of the media object inside the folder 'media/lidar/lidar_scans' which is
        located in the Digital Ocean Spaces S3 bucket. In practice, this should be the name of the object
        i.e. 'kia_seltos_2022.glb'
    Returns:
        binary str: the binary string representing the media object located at the filepath
    """
    client = create_s3_client()
    bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    try:
        response = client.get_object(
            Bucket=bucket, Key=f'media/lidar/lidar_scans/{filepath}')
    except Exception as e:
        print(e)
        raise e
    obj = response['Body']
    return obj
