# cloudaux gcp support

Cloud Auxiliary has support for Google Cloud Platform.

## Documenation

 - [CloudAux](../../README.md "CloudAux Readme")
 - [AWS](../aws/README.md "Amazon Web Services Docs")
 - [GCP](README.md "Google Cloud Platform Docs") [THIS FILE]

## Features

 - choosing the best client based on service
 - client caching
 - general caching and stats decorators available
 - basic support for non-specified discovery-API services

## Orchestration Supported Technologies

 - IAM Service Accounts
 - Network/Subnetworks
 - Storage Buckets

## Install

    pip install cloudaux

## Authentication/Authorization

 - Default Credentials (if running on GCE)
 - JSON key format

## Example

    # directly asking for a client:
    from cloudaux.aws.gcp.auth import get_client
    client = get_client('gce', **conn_details)
   
    # Over your entire environment:
    from cloudaux.gcp.decorators import iter_project
   
    projects = ['my-project-one', 'my-project-two']

    # To specify per-project key_files, you can do thie following:
    # projects = [
    #  {'project': 'my-project-one', key_file='/path/to/project-one.json'},
    #  {'project': 'my-project-two', key_file='/path/to/project-two.json'}
    # ]
    #
    # To specify a single key_file for all projects, use the key_file argument
    # to the decorator
    # @iter_project(projects=projects, key_file='/path/to/key.json')
    #
    # To use default credentials, omit the key_file argument
    # @iter_project(projects=projects)
    
    @iter_project(projects=projects, key_file='/path/to/key.json')
    def test_iter(**kwargs):
       accounts = list_serviceaccounts(**kwargs)
       ret = []
       for account in accounts:
         ret.append(get_serviceaccount_complete(service_account=account['name']))
       return ret

## Orchestration Example

### IAM Service Account

    from cloudaux.orchestration.gcp.iam.serviceaccount import get_serviceaccount_complete
    sa_name = 'projects/my-project-one/serviceAccounts/service-account-key@my-project-one.iam.gserviceaccount.com'
    sa = get_serviceaccount_complete(sa_name, **conn_details)
    print(json.dumps(sa, indent=4, sort_keys=True))

    {
      "DisplayName": "service-account", 
      "Email": "service-account@my-project-one.iam.gserviceaccount.com", 
      "Etag": "BwUzTDvWgHw=", 
      "Keys": [
          {
              "KeyAlgorithm": "KEY_ALG_RSA_2048", 
              "Name": "projects/my-project-one/serviceAccounts/service-account@my-project-one.iam.gserviceaccount.com/keys/8be0096886f6ed5cf51abb463d3448c8aee6c6b6", 
              "ValidAfterTime": "2016-06-30T18:26:45Z", 
              "ValidBeforeTime": "2026-06-28T18:26:45Z"
          }, 
 	  ...
      ], 
      "Name": "projects/my-project-one/serviceAccounts/service-account@my-project-one.iam.gserviceaccount.com", 
      "Oauth2ClientId": "115386704809902483492", 
      "Policy": [
          {
              "Members": [
                  "user:test-user@gmail.com"
              ], 
              "Role": "roles/iam.serviceAccountActor"
          }
      ], 
      "ProjectId": "my-project-one", 
      "UniqueId": "115386704809902483492"
    }
    
### Network
    from cloudaux.orchestration.gcp.gce.network import get_network_and_subnetworks
    net_subnet = get_network_and_subnetworks(network=NETWORK, **conn_details)
    print(json.dumps(net_subnet, indent=4, sort_keys=True))

    {
      "AutoCreateSubnetworks": true, 
      "CreationTimestamp": "2016-05-09T11:15:47.434-07:00", 
      "Description": "Default network for the project", 
      "Id": "5748627682906434876", 
      "Kind": "compute#network", 
      "Name": "default", 
      "SelfLink": "https://www.googleapis.com/compute/v1/projects/my-project-one/global/networks/default", 
      "Subnetworks": [
          {
              "CreationTimestamp": "2016-10-25T09:53:00.777-07:00", 
              "GatewayAddress": "10.146.0.1", 
              "Id": "1852214226435846915", 
              "IpCidrRange": "10.146.0.0/20", 
              "Kind": "compute#subnetwork", 
              "Name": "default", 
              "Network": "https://www.googleapis.com/compute/v1/projects/my-project-one/global/networks/default", 
              "Region": "https://www.googleapis.com/compute/v1/projects/my-project-one/regions/asia-northeast1", 
              "SelfLink": "https://www.googleapis.com/compute/v1/projects/my-project-one/regions/asia-northeast1/subnetworks/default"
          }, 
          ...
      ]
    }

### GCS Bucket
    from cloudaux.orchestration.gcp.gcs.bucket import get_bucket
    b = get_bucket(bucket_name=BUCKET, **conn_details)
    print(json.dumps(b, indent=4, sort_keys=True))

    {
	"Acl": [
          {
              "entity": "project-editors-2094195755361",
              "role": "OWNER"
          }, 
          {
              "entity": "project-viewers-2094195755361",
              "role": "READER"
          }, 
          {
              "entity": "project-owners-2094195755361",
              "role": "OWNER"
          }
        ],
        "Cors": [],
        "DefaultObjectAcl": [
          {
              "entity": "project-editors-1094195755360",
              "role": "OWNER"
          },
          {
              "entity": "project-viewers-1094195755360",
              "role": "READER"
          }
        ],
        "Etag": "CAE=",
        "Id": "my-bucket",
        "Location": "US",
        "Metageneration": 1,
        "Owner": null,
        "Path": "/b/my-bucket",
        "ProjectNumber": 2094195755361,
        "SelfLink": "https://www.googleapis.com/storage/v1/my-bucket",
        "StorageClass": "MULTI_REGIONAL",
        "VersioningEnabled": false
    }
## Firewall Rules
### List Rules
    from cloudaux.gcp.gce.firewall import list_firewall_rules
    rules = list_firewall_rules(**conn_details)
    for rule in rules:
      print(json.dumps(rule, indent=4, sort_keys=True))

### Get Single Rule
    # get single rule
    from cloudaux.gcp.gce.firewall import get_firewall_rule
    rule = get_firewall_rule(Firewall='default-allow-http', **conn_details)
    print(json.dumps(rule, indent=4, sort_keys=True))

    {
        "allowed": [
            {
                "IPProtocol": "tcp",
                "ports": [
                    "80"
                ]
            }
        ],
        "creationTimestamp": "2016-10-03T11:10:37.412-07:00",
        "description": "",
        "id": "6048401367777616399",
        "kind": "compute#firewall",
        "name": "default-allow-http",
        "network": "https://www.googleapis.com/compute/v1/projects/my-project/global/networks/default",
        "selfLink": "https://www.googleapis.com/compute/v1/projects/my-project/global/firewalls/default-allow-http",
        "sourceRanges": [
            "0.0.0.0/0"
        ],
        "targetTags": [
            "http-server"
        ]
    }

## Function Stats
    from cloudaux.gcp.utils import get_gcp_stats
    print json.dumps(get_gcp_stats(), indent=4)

    {
       "n=get_client__args=('gce',)__kwargs={'project': 'my-project-one', 'key_file': None, 'service_type': 'client', 'http_auth': None}": [
           0.12389707565307617,
           4.506111145019531e-05,
           4.506111145019531e-05,
           4.601478576660156e-05,
           4.100799560546875e-05,
           5.793571472167969e-05
       ],
      ...
    }
## Caching Stats
### Access Details
    from cloudaux.gcp.utils import get_cache_access_details
    print get_cache_access_details(key=KEY)
    {
      "n=get_client__args=('gce',)__kwargs={'project': 'my-project-one', 'key_file': None, 'service_type': 'client', 'http_auth': None}":
        {'miss': 1,
	 'expired': 0,
	  'hit': 5}
       ...
    }

### Totals
    from cloudaux.gcp.utils import get_cache_stats
    print json.dumps(get_cache_stats(), indent=4)

    {
        "totals": {
            "keys": 3,
            "miss": 3,
            "expired": 0,
            "hit": 30
        }
    }
