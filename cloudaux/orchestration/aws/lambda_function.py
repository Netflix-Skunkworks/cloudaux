from cloudaux.aws.lambda_function import *
from cloudaux.decorators import modify_output
from flagpole import FlagRegistry, Flags
import json


registry = FlagRegistry()
FLAGS = Flags('BASE', 'ALIASES', 'EVENT_SOURCE_MAPPINGS', 'VERSIONS', 'TAGS', 'POLICY')


@registry.register(flag=FLAGS.POLICY, depends_on=FLAGS.VERSIONS, key='policy')
def _get_policy(lambda_function, **conn):
    """Get LambdaFunction Policies.  (there can be many of these!)
    
    Lambda Function Policies are overly complicated.  They can be attached to a label,
    a version, and there is also a default policy.
    
    This method attempts to gather all three types.
    """
    policies = dict(Versions=dict(), Aliases=dict())

    for version in [v['Version'] for v in lambda_function['versions']]:
        try:
            policies['Versions'][version] = get_policy(FunctionName=lambda_function['FunctionName'], Qualifier=version, **conn)
        except:
            pass

    for alias in [v['Name'] for v in lambda_function['aliases']]:
        try:
            policies['Aliases'][alias] = json.loads(
                get_policy(FunctionName=lambda_function['FunctionName'], Qualifier=alias, **conn))
        except Exception as e:
            pass

    policies['DEFAULT'] = json.loads(get_policy(FunctionName=lambda_function['FunctionName'], **conn))
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
    return list_event_source_mappings(FunctionName=lambda_function['FunctionName'], **conn)


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
        lambda_function = get_function(FunctionName=lambda_function['FunctionName'], **conn)
        
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
    if isinstance(lambda_function, basestring):
        from cloudaux.orchestration.aws.arn import ARN
        lambda_function_arn = ARN(lambda_function)
        if lambda_function_arn.error:
            lambda_function = dict(FunctionName=lambda_function)
        else:
            lambda_function = dict(FunctionName=lambda_function_arn.name)

    return registry.build_out(flags, start_with=lambda_function, pass_datastructure=True, **conn)