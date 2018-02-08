import logging
import time
import boto

from django.conf import settings


logger = logging.getLogger(__name__)


class S3Handler:
    """
    This class acts a wrapper for S3 URL Signing
    """

    def __init__(self, name=None):
        """
        Creates the object for signing URLS

        arguments:
        name -- (String) Name of the S3 bucket

        """
        if name is None:
            self.bucketRoute = settings.CSV_S3_BUCKET_NAME
        else:
            self.bucketRoute = name

        S3Handler.REGION = settings.CSV_AWS_REGION

    def get_simple_url(self, file_name):
        """
        Gets URL for read
        """

        s3connection = boto.s3.connect_to_region(S3Handler.REGION)
        generated = "https://{}/{}/{}".format(s3connection.server_name(), self.bucketRoute, file_name)
        return generated

    @staticmethod
    def get_timestamped_filename(filename):
        """
        Gets a Timestamped file name to prevent conflicts on S3 Uploading
        """
        seconds = str(time.time() - 1500000000).replace('.', '_')
        return '{}_{}'.format(seconds, filename)
