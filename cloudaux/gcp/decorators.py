"""
.. module: cloudaux.gcp.decorators
    :platform: Unix
    :copyright: (c) 2016 by Google Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Tom Melendez (@supertom) <supertom@google.com>
"""
import time
from functools import wraps

from six import string_types

from cloudaux.gcp.gcpcache import GCPCache
from cloudaux.gcp.utils import get_creds_from_kwargs, rewrite_kwargs

_GCP_STATS = {}
_GCP_CACHE = GCPCache()


def _build_key(func_name, args, kwargs):
    """Builds key for cache and stats."""
    return "n=%s__args=%s__kwargs=%s" % (func_name, args, kwargs)


def gcp_conn(service, service_type='client', future_expiration_minutes=15):
    """
    service_type: not currently used.
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Import here to avoid circular import issue
            from cloudaux.gcp.auth import get_client
            (conn_args, kwargs) = get_creds_from_kwargs(kwargs)
            client_details, client = get_client(
                service, service_type=service_type,
                future_expiration_minutes=15, **conn_args)
            kwargs = rewrite_kwargs(client_details['client_type'], kwargs,
                                    client_details['module_name'])
            kwargs['client'] = client
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def gcp_stats():
    """
    Collect stats

    Specifically, time function calls
    :returns: function response
    :rtype: varies
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            result = f(*args, **kwargs)
            end_time = time.time()
            strkey = _build_key(f.__name__, args, kwargs)
            _GCP_STATS.setdefault(strkey, []).append(end_time - start_time)
            return result

        return decorated_function

    return decorator


def gcp_cache(future_expiration_minutes=15):
    """
    Cache function output
    :param future_expiration_minutes: Number of minutes in the future until item
                                      expires.  Default is 15.
    :returns: function response, optionally from the cache
    :rtype: varies
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            strkey = _build_key(f.__name__, args, kwargs)
            cached_result = _GCP_CACHE.get(strkey)
            if cached_result:
                return cached_result
            else:
                result = f(*args, **kwargs)
                _GCP_CACHE.insert(strkey, result, future_expiration_minutes)
            return result

        return decorated_function

    return decorator


def iter_project(projects, key_file=None):
    """
    Call decorated function for each item in project list.

    Note: the function 'decorated' is expected to return a value plus a dictionary of exceptions.

    If item in list is a dictionary, we look for a 'project' and 'key_file' entry, respectively.
    If item in list is of type string_types, we assume it is the project string. Default credentials
    will be used by the underlying client library.

    :param projects: list of project strings or list of dictionaries
                     Example: {'project':..., 'keyfile':...}. Required.
    :type projects: ``list`` of ``str`` or ``list`` of ``dict``

    :param key_file: path on disk to keyfile, for use with all projects
    :type key_file: ``str``

    :returns: tuple containing a list of function output and an exceptions map
    :rtype: ``tuple of ``list``, ``dict``
    """

    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            item_list = []
            exception_map = {}
            for project in projects:
                if isinstance(project, string_types):
                    kwargs['project'] = project
                    if key_file:
                        kwargs['key_file'] = key_file
                elif isinstance(project, dict):
                    kwargs['project'] = project['project']
                    kwargs['key_file'] = project['key_file']
                itm, exc = func(*args, **kwargs)
                item_list.extend(itm)
                exception_map.update(exc)
            return (item_list, exception_map)

        return decorated_function

    return decorator
