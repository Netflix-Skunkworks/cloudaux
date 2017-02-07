"""
.. module: cloudaux.orchestration.gcp.gcs.bucket
    :platform: Unix
    :copyright: (c) 2016 by Google Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Tom Melendez (@supertom) <supertom@google.com>
"""
from cloudaux.gcp.gcs import get_bucket as fetch_bucket
from cloudaux.gcp.utils import strdate
from cloudaux.orchestration import modify

def get_bucket(bucket_name, output='camelized', include_created=False, **conn):

    result = {}
    bucket = fetch_bucket(Bucket=bucket_name, **conn)
    if not bucket:
        return modify(dict(Error='Unauthorized'), format=output)

    result['acl'] = list(bucket.acl)
    result['cors'] = bucket.cors
    result['etag'] = bucket.etag
    result['id'] = bucket.id
    result['location'] = bucket.location
    result['metageneration'] = bucket.metageneration
    result['owner'] = bucket.owner
    result['path'] = bucket.path
    result['project_number'] = bucket.project_number
    result['self_link'] = bucket.self_link
    result['storage_class'] = bucket.storage_class
    result['versioning_enabled'] = bucket.versioning_enabled
    if include_created:
        result['time_created'] = strdate(bucket.time_created)

    return modify(result, format=output)
