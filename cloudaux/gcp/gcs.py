"""
.. module: cloudaux.gcp.gcs
    :platform: Unix
    :copyright: (c) 2016 by Google Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Tom Melendez (@supertom) <supertom@google.com>
"""
from cloudaux.gcp.decorators import gcp_conn

@gcp_conn('gcs')
def list_buckets(client=None, **kwargs):
    """
    List buckets for a project.

    :param client: client object to use.
    :type client: Google Cloud Storage client

    :returns: list of dictionary reprsentation of Bucket
    :rtype: ``list`` of ``dict``
    """
    buckets = client.list_buckets(**kwargs)
    return [b.__dict__ for b in buckets]

@gcp_conn('gcs')
def get_bucket(client=None, **kwargs):
    """
    Get bucket object.

    :param client: client object to use.
    :type client: Google Cloud Storage client

    :returns: Bucket object
    :rtype: ``object``
    """
    bucket = client.lookup_bucket(kwargs['Bucket'])
    return bucket
    
def get_bucket_field(**kwargs):
    """
    Get value from member field of bucket object.

    :param Field: name of member of Bucket object to return.
    :type Field: ``str``

    :returns: value contained by the specified member field.
    :rtype: varies
    """
    bucket = get_bucket(**kwargs)
    if bucket:
        return getattr(bucket, kwargs['Field'], None)
    else:
        return None

def list_objects_in_bucket(**kwargs):
    """
    List objects in bucket.

    :param Bucket: name of bucket
    :type Bucket: ``str``

    :returns list of objects in bucket
    :rtype: ``list``
    """
    bucket = get_bucket(**kwargs)
    if bucket:
        return [o for o in bucket.list_blobs()]
    else:
        return None

def get_object_in_bucket(**kwargs):
    """
    Retrieve object from Bucket.

    :param Bucket: name of bucket
    :type Bucket: ``str``

    :returns: object from bucket or None
    :rtype ``object`` or None
    """
    bucket = get_bucket(**kwargs)
    if bucket:
        return bucket.get_blob(kwargs['Object'])
    else:
        return None
