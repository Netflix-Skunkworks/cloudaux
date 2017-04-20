from cloudaux.gcp.iam import get_iam_policy, get_serviceaccount, get_serviceaccount_keys
from cloudaux.orchestration.gcp.utils import list_modify, modify
from cloudaux.orchestration.flag_registry import FlagRegistry
from bunch import Bunch


FLAGS=Bunch(
    KEYS=1,
    POLICY=2,
    ALL=3)


class SAFlagRegistry(FlagRegistry):
    from collections import defaultdict
    r = defaultdict(list)


@SAFlagRegistry.register(flag=FLAGS.KEYS, key='keys')
def get_keys(service_account, output, **conn):
    keys = get_serviceaccount_keys(service_account=service_account, **conn)
    if keys: 
        return list_modify(keys, output)
    return None


@SAFlagRegistry.register(flag=FLAGS.POLICY, key='policy')
def get_policy(service_account, output, **conn):
    policy = get_iam_policy(service_account=service_account, **conn)
    if policy:
         return list_modify(policy, output)
    return None


def get_serviceaccount_complete(service_account, output='camelized', flags=FLAGS.ALL, **conn):
    result = get_serviceaccount(service_account=service_account, **conn)
    if result:
        SAFlagRegistry.build_out(result, flags, service_account, output, **conn)
        return modify(result, format=output)
    return None

