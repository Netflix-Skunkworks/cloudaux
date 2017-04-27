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
from cloudaux.orchestration.flag_registry import FlagRegistry, Flags


class GCSFlagRegistry(FlagRegistry):
    from collections import defaultdict
    r = defaultdict(list)


FLAGS = Flags('BASE')


@GCSFlagRegistry.register(flag=FLAGS.BASE)
def _get_base(bucket_name, **conn):
    bucket = fetch_bucket(Bucket=bucket_name, **conn)
    if not bucket:
        return modify(dict(Error='Unauthorized'), format=output)

    result['acl'] = list(bucket.acl)
    result['default_object_acl'] = list(bucket.default_object_acl)
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
    result['time_created'] = strdate(bucket.time_created)
    result['_version'] = 1
    return result


def get_bucket(bucket_name, output='camelized', flags=FLAGS.ALL, **conn):
    result = dict()
    GCSFlagRegistry.build_out(result, flags, bucket_name, **conn)
    return modify(result, format=output)
