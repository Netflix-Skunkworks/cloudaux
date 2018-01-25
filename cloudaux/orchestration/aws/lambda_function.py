from cloudaux.aws.lambda_function import *
from cloudaux.decorators import modify_output
from flagpole import FlagRegistry, Flags
import json

from cloudaux.orchestration.aws import ARN

registry = FlagRegistry()
FLAGS = Flags('BASE', 'ALIASES', 'EVENT_SOURCE_MAPPINGS', 'VERSIONS', 'TAGS', 'POLICY')


@registry.register(flag=FLAGS.POLICY, depends_on=FLAGS.VERSIONS, key='policy')
def _get_policy(lambda_function, **conn):
    """Get LambdaFunction Policies.  (there can be many of these!)
    
    Lambda Function Policies are overly complicated.  They can be attached to a label,
    a version, and there is also a default policy.
    
    This method attempts to gather all three types.
    
    AWS returns an exception if the policy requested does not exist.  We catch and ignore these exceptions.
    """
    policies = dict(Versions=dict(), Aliases=dict(), DEFAULT=dict())

    for version in [v['Version'] for v in lambda_function['versions']]:
        try:
            policies['Versions'][version] = get_policy(FunctionName=lambda_function['FunctionName'], Qualifier=version, **conn)
            policies['Versions'][version] = json.loads(policies['Versions'][version])
        except Exception as e:
            pass

    for alias in [v['Name'] for v in lambda_function['aliases']]:
        try:
            policies['Aliases'][alias] = get_policy(FunctionName=lambda_function['FunctionName'], Qualifier=alias, **conn)
            policies['Aliases'][alias] = json.loads(policies['Aliases'][alias])
        except Exception as e:
            pass

    try:
        policies['DEFAULT'] = get_policy(FunctionName=lambda_function['FunctionName'], **conn)
        policies['DEFAULT'] = json.loads(policies['DEFAULT'])
    except Exception as e:
        pass

    return policies


@registry.register(flag=FLAGS.ALIASES, key='aliases')
def _get_aliases(lambda_function, **conn):
    return list_aliases(FunctionName=lambda_function['FunctionName'], **conn)


@registry.register(flag=FLAGS.TAGS, depends_on=FLAGS.BASE, key='tags')
def _get_tags(lambda_function, **conn):
    return list_tags(Resource=lambda_function['FunctionArn'], **conn)


@registry.register(flag=FLAGS.VERSIONS, depends_on=FLAGS.ALIASES, key='versions')
def _get_versions(lambda_function, **conn):
    return list_versions_by_function(FunctionName=lambda_function['FunctionName'], **conn)


@registry.register(flag=FLAGS.EVENT_SOURCE_MAPPINGS, key='event_source_mappings')
def _get_event_source_mappings(lambda_function, **conn):
    mappings = list_event_source_mappings(FunctionName=lambda_function['FunctionName'], **conn)
    for mapping in mappings:
        if 'LastModified' in mapping:
            mapping['LastModified'] = str(mapping['LastModified'])
    return mappings


@registry.register(flag=FLAGS.BASE)
def get_base(lambda_function, **conn):
    base_fields = frozenset(
        ['FunctionName', 'FunctionArn', 'Runtime', 'Role', 'Handler'
        'CodeSize', 'Description', 'Timeout', 'MemorySize', 'LastModified',
        'CodeSha256', 'Version', 'VpcConfig', 'DeadLetterConfig', 'Environment',
        'KMSKeyArn', 'TracingConfig', 'MasterArn'])
    needs_base = False

    for field in base_fields:
        if field not in lambda_function:
            needs_base = True
            break

    if needs_base:
        lambda_function = get_function_configuration(FunctionName=lambda_function['FunctionName'], **conn)
        lambda_function.pop('ResponseMetadata', None)

    # Copy FunctionArn to just Arn
    lambda_function.update({
        'Arn': lambda_function.get('FunctionArn'),
        '_version': 1
    })
    return lambda_function


@modify_output
def get_lambda_function(lambda_function, flags=FLAGS.ALL, **conn):
    """Fully describes a lambda function.
    
    Args:
        lambda_function: Name, ARN, or dictionary of lambda function. If dictionary, should likely be the return value from list_functions. At a minimum, must contain a key titled 'FunctionName'.
        flags: Flags describing which sections should be included in the return value. Default ALL
    
    Returns:
        dictionary describing the requested lambda function.
    """
    # Python 2 and 3 support:
    try:
        basestring
    except NameError as _:
        basestring = str

    # If STR is passed in, determine if it's a name or ARN and built a dict.
    if isinstance(lambda_function, basestring):
        lambda_function_arn = ARN(lambda_function)
        if lambda_function_arn.error:
            lambda_function = dict(FunctionName=lambda_function)
        else:
            lambda_function = dict(FunctionName=lambda_function_arn.name, FunctionArn=lambda_function)

    # If an ARN is available, override the account_number/region from the conn dict.
    if 'FunctionArn' in lambda_function:
        lambda_function_arn = ARN(lambda_function['FunctionArn'])
        if not lambda_function_arn.error:
            if lambda_function_arn.account_number:
                conn['account_number'] = lambda_function_arn.account_number
            if lambda_function_arn.region:
                conn['region'] = lambda_function_arn.region

    return registry.build_out(flags, start_with=lambda_function, pass_datastructure=True, **conn)