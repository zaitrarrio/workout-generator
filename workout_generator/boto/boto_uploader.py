import boto

from boto.exception import S3ResponseError
from django.conf import settings

from .constants import BUCKET_NAME

ACCESS_KEY = settings.AWS_ACCESS_KEY_ID
SECRET_KEY = settings.AWS_SECRET_ACCESS_KEY


POOL_SIZE = 16
ASYNC = True

PROGRESS_INTERVAL = 5
IGNORED_FILES = {
    ".DS_Store"
}
ACCEPTABLE_FILENAMES = {
    "jpg",
    "JPG",
    "jpeg",
    "JPEG"
}

# TODO: need to make a group policy right here
S3_ACL = "bucket-owner-full-control"


class BotoUploader(object):

    def __init__(self, read_directory, make_public=False):
        self.read_directory = read_directory
        self.make_public = make_public
        self.files_uploaded = []

    @classmethod
    def _make_key(cls, write_amazon_filename):
        connection = cls._get_connection()
        bucket = cls._get_or_create_bucket(connection, BUCKET_NAME)
        key_name = write_amazon_filename
        key = bucket.get_key(key_name)
        if key is None:
            key = bucket.new_key(key_name)
        return key

    @classmethod
    def upload_single_file(cls, read_hard_drive_filename, write_amazon_filename):
        key = cls._make_key(write_amazon_filename)
        print "Starting upload of %s" % read_hard_drive_filename
        key.set_contents_from_filename(read_hard_drive_filename,
                                       replace=True,
                                       reduced_redundancy=False)
        key.make_public()

        return "%s/%s" % (BUCKET_NAME, write_amazon_filename)

    @classmethod
    def upload_single_file_from_memory(cls, in_mem_file, write_amazon_filename):
        key = cls._make_key(write_amazon_filename)
        key.set_contents_from_file(in_mem_file,
                                   replace=True,
                                   reduced_redundancy=False)
        key.make_public()
        return "%s/%s" % (BUCKET_NAME, write_amazon_filename)

    def progress_reporter(self, bytes_transfered, bytes_sent, filename):
        percent_finished = 0
        if bytes_sent:
            percent_finished = (100 * bytes_transfered) / bytes_sent
        print "%s: %s%%" % (filename, percent_finished)

    @classmethod
    def _get_or_create_bucket(cls, connection, name):
        """Retrieves a bucket if it exists, otherwise creates it."""
        try:
            return connection.get_bucket(name)
        except S3ResponseError:
            return connection.create_bucket(name)  # , policy=S3_ACL)

    @classmethod
    def _get_connection(cls):
        conn = boto.connect_s3(aws_access_key_id=ACCESS_KEY,
                            aws_secret_access_key=SECRET_KEY)
        return conn

    def _standard_transfer(self, bucket, filename):
        print "Uploading %s to %s" % (filename, bucket)
        key_name = filename.replace(self.read_directory, "", 1)
        key = bucket.get_key(key_name)
        if key is None:
            key = bucket.new_key(key_name)
        else:
            print "File: %s already exists on Amazon." % filename
            return

        def dynamic_progress_reporter(bytes_transfered, bytes_sent):
            f = filename
            self.progress_reporter(bytes_transfered, bytes_sent, f)

        key.set_contents_from_filename(filename, replace=True,
                                       cb=dynamic_progress_reporter,
                                       num_cb=PROGRESS_INTERVAL,
                                       reduced_redundancy=False)
        if self.make_public:
            key.make_public()
        self.files_uploaded.append(key_name)
        print "Finished transferring %s" % filename

    def upload(self, filename):
        connection = self._get_connection()
        bucket = self._get_or_create_bucket(connection, BUCKET_NAME)
        self._standard_transfer(bucket, filename)
        self._remove_file(filename)
