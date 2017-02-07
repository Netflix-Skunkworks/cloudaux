from cloudaux.gcp.iam import get_iam_policy, get_serviceaccount, get_serviceaccount_keys
from cloudaux.orchestration.gcp.utils import list_modify, modify

def get_serviceaccount_complete(service_account, output='camelized', **conn):
    sa = get_serviceaccount(service_account=service_account, **conn)
    if sa:
        full_sa = sa
        keys = get_serviceaccount_keys(service_account=service_account, **conn)
        if keys:
            full_sa['keys'] = list_modify(keys, output)

        policy = get_iam_policy(service_account=service_account, **conn)
        if policy:
            full_sa['policy'] = list_modify(policy, output)
        return modify(full_sa, format=output)
    else:
        return None
    

    
