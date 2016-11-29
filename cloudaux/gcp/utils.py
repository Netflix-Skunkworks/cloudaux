"""
.. module: cloudaux.gcp.utils
    :platform: Unix
    :copyright: (c) 2016 by Google Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Tom Melendez (@supertom) <supertom@google.com>
"""
def strdate(dte):
    return dte.strftime('%Y-%m-%dT%H:%M:%SZ')


def get_creds_from_kwargs(kwargs):
    """Helper to get creds out of kwargs."""
    creds = {
        'key_file': kwargs.pop('key_file', None),
        'http_auth': kwargs.pop('http_auth', None),
        'project': kwargs.get('project', None)
    }
    return (creds, kwargs)


def rewrite_kwargs(conn_type, kwargs, module_name=None):
    """
    Manipulate connection keywords.
    
    Modifieds keywords based on connection type.

    Current modifications:
    - if conn_type is not cloud and module is 'compute', 
      then rewrite project as name.

    :param conn_type: E.g. 'cloud' or 'general'
    :type conn_type: ``str``

    :param kwargs: Dictionary of keywords sent in by user.
    :type kwargs: ``dict``

    :param module_name: Name of specific module that will be loaded.
                        Default is None.
    :type conn_type: ``str`` or None

    :returns kwargs with client and module specific changes
    :rtype: ``dict``
    """
    if conn_type != 'cloud' and module_name != 'compute':
        if 'project' in kwargs:
            kwargs['name'] = 'projects/%s' % kwargs.pop('project')
    return kwargs


def gce_list_aggregated(service=None, key_name='name', **kwargs):
    """General aggregated list function for the GCE service."""
    resp_list = []
    req = service.aggregatedList(**kwargs)

    while req is not None:
        resp = req.execute()
        for location, item in resp['items'].items():
            if key_name in item:
                resp_list.extend(item[key_name])
            
        req = service.aggregatedList_next(previous_request=req,
                                           previous_response=resp)
    return resp_list


def gce_list(service=None, **kwargs):
    """General list function for the GCE service."""
    resp_list = []
    req = service.list(**kwargs)

    while req is not None:
        resp = req.execute()
        for item in resp['items']:
            resp_list.append(item)
        req = service.list_next(previous_request=req,
                                 previous_response=resp)
    return resp_list


def service_list(service=None, key_name=None, **kwargs):
    """General list function for Google APIs."""
    resp_list = []
    req = service.list(**kwargs)

    while req is not None:
        resp = req.execute()
        if key_name and key_name in resp:
            resp_list.extend(resp[key_name])
        else:
            resp_list.append(resp)
        # Not all list calls have a list_next
        if hasattr(service, 'list_next'):
            req = service.list_next(previous_request=req,
                                    previous_response=resp)
        else:
            req = None
    return resp_list


def get_cache_stats():
    """Helper to retrieve stats cache."""
    from cloudaux.gcp.decorators import _GCP_CACHE
    return _GCP_CACHE.get_stats()


def get_cache_access_details(key=None):
    """Retrieve detailed cache information."""
    from cloudaux.gcp.decorators import _GCP_CACHE
    return _GCP_CACHE.get_access_details(key=key)


def get_gcp_stats():
    """Retrieve stats, such as function timings."""
    from cloudaux.gcp.decorators import _GCP_STATS
    return _GCP_STATS
