from cloudaux.aws.glacier import describe_vault, get_vault_access_policy, list_tags_for_vault
from cloudaux.decorators import modify_output
from cloudaux.orchestration.aws.arn import ARN
from flagpole import FlagRegistry, Flags
from six import string_types

registry = FlagRegistry()
FLAGS = Flags('BASE', 'POLICY', 'TAGS')


@registry.register(flag=FLAGS.BASE)
def _get_base(vault_obj, **conn):
    base_fields = ['VaultARN', 'VaultName', 'CreationDate', 'NumberOfArchives', 'SizeInBytes']

    if not all(field in vault_obj for field in base_fields):
        vault_obj = describe_vault(vault_name=vault_obj['VaultName'], **conn)

    vault_obj['_version'] = 1
    # sometimes it's expected that the item contains 'Arn' and not 'VaultARN'
    vault_obj['Arn'] = vault_obj['VaultARN']
    return vault_obj


@registry.register(flag=FLAGS.POLICY, key='Policy')
def _get_vault_access_policy(vault_obj, **conn):
    return get_vault_access_policy(vault_name=vault_obj['VaultName'], **conn)


@registry.register(flag=FLAGS.TAGS, key='Tags')
def _list_tags_for_vault(vault_obj, **conn):
    return list_tags_for_vault(vault_name=vault_obj['VaultName'], **conn)


@modify_output
def get_vault(vault_obj, flags=FLAGS.ALL, **conn):
    """
    Orchestrates calls to build a Glacier Vault in the following format:

    {
        "VaultARN": ...,
        "VaultName": ...,
        "CreationDate" ...,
        "LastInventoryDate" ...,
        "NumberOfArchives" ...,
        "SizeInBytes" ...,
        "Policy" ...,
        "Tags" ...
    }
    Args:
        vault_obj: name, ARN, or dict of Glacier Vault
        flags: Flags describing which sections should be included in the return value. Default ALL

    Returns:
        dictionary describing the requested Vault
    """
    if isinstance(vault_obj, string_types):
        vault_arn = ARN(vault_obj)
        if vault_arn.error:
            vault_obj = {'VaultName': vault_obj}
        else:
            vault_obj = {'VaultName': vault_arn.parsed_name}

    return registry.build_out(flags, vault_obj, **conn)
