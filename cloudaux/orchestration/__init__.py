from inflection import camelize, underscore


def _modify(item, func):
    """
    Modifies each item.keys() string based on the func passed in.
    Often used with inflection's camelize or underscore methods.

    :param item: dictionary representing item to be modified
    :param func: function to run on each key string
    :return: dictionary where each key has been modified by func.
    """
    result = dict()
    for key in item:
        result[func(key)] = item[key]
    return result


def modify(item, output='camelized'):
    """
    Calls _modify and either passes the inflection.camelize method or the inflection.underscore method.

    :param item: dictionary representing item to be modified
    :param output: string 'camelized' or 'underscored'
    :return:
    """
    if output == 'camelized':
        return _modify(item, camelize)
    elif output == 'underscored':
        return _modify(item, underscore)