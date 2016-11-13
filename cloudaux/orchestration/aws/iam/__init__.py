from inflection import camelize, underscore

from cloudaux.orchestration.aws.arn import ARN
from cloudaux.exceptions import CloudAuxException


def _conn_from_args(item, conn):
    if item.get('Arn'):
        conn.update(_conn_from_arn(item.get('Arn')))
    elif item.get('AccountNumber'):
        conn.update({'account_number': item['AccountNumber']})
        del item['AccountNumber']


def _conn_from_arn(arn):
    """
    Extracts the account number from an ARN.
    :param arn: Amazon ARN containing account number.
    :return: dictionary with a single account_number key that can be merged with an existing
    connection dictionary containing fields such as assume_role, session_name, region.
    """
    role_arn = ARN(arn)
    if role_arn.error:
        raise CloudAuxException('Bad ARN: {arn}'.format(arn=arn))
    return dict(
        account_number=role_arn.account_number,
    )


def _get_name_from_structure(item, default):
    """
    Given a possibly sparsely populated item dictionary, try to retrieve the item name.
    First try the default field.  If that doesn't exist, try to parse the from the ARN.
    :param item: dict containing (at the very least) item_name and/or arn
    :return: item name
    """
    if item.get(default):
        return item.get(default)

    if item.get('Arn'):
        arn = item.get('Arn')
        item_arn = ARN(arn)
        if item_arn.error:
            raise CloudAuxException('Bad ARN: {arn}'.format(arn=arn))
        return item_arn.parsed_name

    raise CloudAuxException('Cannot extract item name from input: {input}.'.format(input=item))


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
