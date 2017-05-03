from cloudaux.gcp.iam import get_iam_policy, get_serviceaccount, get_serviceaccount_keys
from cloudaux.orchestration import modify
from flagpole import FlagRegistry, Flags


registry = FlagRegistry()
FLAGS = Flags('BASE', 'KEYS', 'POLICY')


@registry.register(flag=FLAGS.KEYS, key='keys')
def get_keys(service_account, **conn):
    return get_serviceaccount_keys(service_account=service_account, **conn)


@registry.register(flag=FLAGS.POLICY, key='policy')
def get_policy(service_account, **conn):
    return get_iam_policy(service_account=service_account, **conn)


@registry.register(flag=FLAGS.BASE)
def _get_base(service_account, **conn):
    sa = get_serviceaccount(service_account=service_account, **conn)
    sa['_version'] = 1
    return sa


def get_serviceaccount_complete(service_account, output='camelized', flags=FLAGS.ALL, **conn):
    result = dict()
    registry.build_out(result, flags, service_account, **conn)
    return modify(result, format=output)
