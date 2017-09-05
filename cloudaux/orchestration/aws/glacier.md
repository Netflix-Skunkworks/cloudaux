# CloudAux AWS Lambda Function

CloudAux can build out a JSON object describing an AWS Glacier Vault.

## Example

    from cloudaux.orchestration.aws.glacier import get_vault

    conn = dict(
        account_number='111111111111',
        assume_role='SecurityMonkey')

    vault = get_vault('MyVault', **conn)
    
    print(json.dumps(provider, indent=2, sort_keys=True))

    {
      "ARN": "arn:aws:glacier:us-east-1:111111111111:vaults/MyVault",
      "CreationDate": "2014-01-27T18:31:49.143Z",
      "LastInventoryDate": "",
      "NumberOfArchives": 0,
      "Policy": "",
      "SizeInBytes": 0,
      "Tags": {},
      "VaultARN": "arn:aws:glacier:us-east-1:111111111111:vaults/MyVault",
      "VaultName": "MyVault"
    }

## Flags

The `get_vault` command accepts flags describing what parts of the structure to build out.

    from cloudaux.orchestration.aws.glacier import FLAGS

    desired_fields = FLAGS.DESCRIBE | FLAGS.TAGS
    vault = get_vault('MyVaultName', flags=desired_flags, **conn)

If not provided, `get_vault` assumes `FLAGS.ALL`.

- BASE - VaultARN, VaultName, CreationDate, SizeInBytes, NumberOfArchives, and Cloudaux implementation number
- TAGS - any tags applied to the vault
- POLICY - a Vault access policy (if defined)
- ALL - all items
