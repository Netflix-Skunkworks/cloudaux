from cloudaux.gcp.iam import get_iam_policy, get_serviceaccount, get_serviceaccount_keys
from cloudaux.decorators import modify_output
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


@modify_output
def get_serviceaccount_complete(service_account, flags=FLAGS.ALL, **conn):
    return registry.build_out(flags, service_account, **conn)
