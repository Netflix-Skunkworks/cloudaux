from inflection import camelize, underscore


def _modify(item, func):
    """
    Modifies each item.keys() string based on the func passed in.
    Often used with inflection's camelize or underscore methods.

    :param item: dictionary representing item to be modified
    :param func: function to run on each key string
    :return: dictionary where each key has been modified by func.
    """
    for key in item:
        new_key = func(key)
        if key != new_key:
            item[new_key] = item.pop(key)
    return item


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