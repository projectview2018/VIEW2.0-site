from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    location = 'static'
    default_acl = 'public-read'


class MediaStorage(S3Boto3Storage):
    location = 'media/lidar/lidar_scans'
    # bucket_name =
    # default_acl = None
    file_overwrite = False
