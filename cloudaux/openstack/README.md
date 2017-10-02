# cloudaux OpenStack support

Cloud Auxiliary has support for Openstack.

## Documentation

 - [CloudAux](../../README.md "CloudAux Readme")
 - [OpenStack](README.md "OpenStack Docs") [THIS FILE]
 - [AWS](../aws/README.md "Amazon Web Services Docs")
 - [GCP](../gcp/README.md "Google Cloud Platform Docs")

## Features

 - intelligent connection caching.
 - generalized OpenStack SDK generator usage.
 - orchestrates all the calls required to fully describe an item.
 - control which attributes are returned flags.

## Orchestration Supported Technologies

 - Openstack SDK supported services

## Install

    pip install cloudaux

For OpenStack support run:

    pip install cloudaux\[openstack\]

## Authentication/Authorization

 - Keystone clouds.yaml

## Example

    from cloudaux.openstack.decorators import _connect
    conn = _connect(cloud_name, region, yaml_file):
    
    # Over your entire environment:
    from cloudaux.openstack.decorators import iter_account_region, get_regions

    @iter_account_region(account_regions=get_regions())
    def list_networks(conn=None, service='network', generator='security_groups'):
        from cloudaux.openstack.utils import list_items
        list_items(**kwargs)

## Orchestration Example

### Security Group

    from cloudaux.orchestration.openstack.security_group import get_security_group, FLAGS

    secgroup = get_security_group(result, flags=flags, **kwargs)
        
    # The flags parameter is optional but allows the user to indicate that 
    # only a subset of the full item description is required.
    # Security Group Flag Options:
    #   RULES, INSTANCES (default)
    # For instance: flags=FLAGS.RULES | FLAGS.INSTANCES

    print(json.dumps(secgroup, indent=4, sort_keys=True))

    {
        "assigned_to": [
            {
               "instance_id": "..."
            }
        ],
        "created_at": "...",
        "description": "...",
        "id": "...",
        "location": "...",
        "name": "...",
        "project_id": "...",
        "revision_number": 3,
        "rules": [
            {
                "rule_type": "...",
                "remote_group_id": "...",
                "from_port": "...",
                "description": "...",
                "tags": [],
                "to_port": "...",
                "ethertype": "...",
                "created_at": "...",
                "updated_at": "...",
                "security_group_id": "...",
                "revision_number": 0,
                "tenant_id": "...",
                "project_id": "..."",
                "id": "...",
                "cidr_ip": "...",
                "ip_protocol": "..."
            },
        ],
        "updated_at": "..."
    }