from inflection import camelize, underscore


def _modify(role, func):
    """
    Modifies each role.keys() string based on the func passed in.
    Often used with inflection's camelize or underscore methods.

    :param role: dictionary representing role to be modified
    :param func: function to run on each key string
    :return: dictionary where each key has been modified by func.
    """
    for key in role:
        new_key = func(key)
        if key != new_key:
            role[new_key] = role[key]
            del role[key]
    return role


def modify(role, format='camelized'):
    """
    Calls _modify and either passes the inflection.camelize method or the inflection.underscore method.

    :param role: dictionary representing role to be modified
    :param format: string 'camelized' or 'underscored'
    :return:
    """
    if format == 'camelized':
        return _modify(role, camelize)
    elif format == 'underscored':
        return _modify(role, underscore)