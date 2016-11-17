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
    arn = ARN(arn)
    if arn.error:
        raise CloudAuxException('Bad ARN: {arn}'.format(arn=arn))
    return dict(
        account_number=arn.account_number,
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



