import ConfigParser
import boto
import io
from boto.s3.key import Key

config = ConfigParser.ConfigParser()
config.read("config.ini")

# Retrieve the AWS ACCESS KEYS and bucket name.
AWS_ACCESS_KEY = config.get('S3', 'AccessKey')
AWS_SECRET_ACCESS_KEY = config.get('S3', 'SecretKey')
S3_BUCKET = config.get('S3', 'Bucket')

# Upload the file to the s3 bucket specified above.
def s3_upload(uploaded_file, filename):
    s3conn = boto.connect_s3(AWS_ACCESS_KEY,AWS_SECRET_ACCESS_KEY)
    bucket = s3conn.get_bucket(S3_BUCKET)
    
    k = Key(bucket)
    k.key = filename
    k.content_type = uploaded_file.content_type
    
    if hasattr(uploaded_file,'temporary_file_path'):
        k.set_contents_from_filename(uploaded_file.temporary_file_path())
    else:
        k.set_contents_from_string(uploaded_file.read())

    k.set_canned_acl('public-read')

    return k.generate_url(expires_in=0, query_auth=False)

# Delete the file with id=id from the s3 bucket.
def s3_delete(filename):
    s3conn = boto.connect_s3(AWS_ACCESS_KEY,AWS_SECRET_ACCESS_KEY)
    bucket = s3conn.get_bucket(S3_BUCKET)
    
    k = Key(bucket)
    k.key = filename
    k.delete()

# Used for pre-populating database with already existing documents.
def initializeDocuments():
    s3conn = boto.connect_s3(AWS_ACCESS_KEY,AWS_SECRET_ACCESS_KEY)
    bucket = s3conn.get_bucket(S3_BUCKET)
    return bucket.list()