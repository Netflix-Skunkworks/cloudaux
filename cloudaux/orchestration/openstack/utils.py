"""
.. module: cloudaux.openstack.orchestration.utils
    :platform: Unix
    :copyright: Copyright (c) 2017 AT&T Intellectual Property. All rights reserved. See AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Michael Stair <mstair@att.com>
"""
import inspect

from six import text_type

""" global ignore_list for OpenStack SDK service object members """
ignore_list = [ 'allow_create', 'allow_delete', 'allow_get', 'allow_head',
		'allow_list', 'allow_update', 'patch_update', 'put_create',
		'service', 'base_path', 'resource_key', 'resources_key' ]

def get_item(item, **kwargs):
    """
    API versioning for each OpenStack service is independent. Generically capture
        the public members (non-routine and non-private) of the OpenStack SDK objects.

    Note the lack of the modify_output decorator. Preserving the field naming allows
        us to reconstruct objects and orchestrate from stored items.
    """
    _item = {}
    for k,v in inspect.getmembers(item, lambda a:not(inspect.isroutine(a))):
        if not k.startswith('_') and not k in ignore_list:
            _item[k] = v

    return sub_dict(_item)


""" from security_monkey.common.utils. Need to convert any embedded OpenStack classes
			to their string/JSON representation """

prims = [int, str, text_type, bool, float, type(None)]

def sub_list(l):
    """
    Recursively walk a data-structure sorting any lists along the way.
    Any unknown types get mapped to string representation

    :param l: list
    :return: sorted list, where any child lists are also sorted.
    """
    r = []

    for i in l:
        if type(i) in prims:
            r.append(i)
        elif type(i) is list:
            r.append(sub_list(i))
        elif type(i) is dict:
            r.append(sub_dict(i))
        else:
            r.append(str(i))
    r = sorted(r)
    return r


def sub_dict(d):
    """
    Recursively walk a data-structure sorting any lists along the way.
    Any unknown types get mapped to string representation

    :param d: dict
    :return: dict where any lists, even those buried deep in the structure, have been sorted.
    """
    r = {}
    for k in d:
        if type(d[k]) in prims:
            r[k] = d[k]
        elif type(d[k]) is list:
            r[k] = sub_list(d[k])
        elif type(d[k]) is dict:
            r[k] = sub_dict(d[k])
        else:
            r[k] = str(d[k])
    return r
