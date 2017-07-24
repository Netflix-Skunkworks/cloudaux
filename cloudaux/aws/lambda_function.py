from cloudaux.aws.sts import sts_conn
from cloudaux.aws.decorators import rate_limited, paginated


@sts_conn('lambda')
@paginated('Aliases')
@rate_limited()
def list_aliases(client=None, **kwargs):
    return client.list_aliases(**kwargs)


@sts_conn('lambda')
@paginated('Versions')
@rate_limited()
def list_versions_by_function(client=None, **kwargs):
    return client.list_versions_by_function(**kwargs)


@sts_conn('lambda')
@paginated('EventSourceMappings')
@rate_limited()
def list_event_source_mappings(client=None, **kwargs):
    return client.list_event_source_mappings(**kwargs)


@sts_conn('lambda')
@rate_limited()
def list_tags(client=None, **kwargs):
    return client.list_tags(**kwargs)['Tags']


@sts_conn('lambda')
@rate_limited()
def get_function_configuration(client=None, **kwargs):
    return client.get_function_configuration(**kwargs)


@sts_conn('lambda')
@rate_limited()
def get_policy(client=None, **kwargs):
    return client.get_policy(**kwargs)['Policy']


@sts_conn('lambda')
@paginated('Functions')
@rate_limited()
def list_functions(client=None, **kwargs):
    return client.list_functions(**kwargs)