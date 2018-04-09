# CloudAux AWS VPC

CloudAux can build out a JSON object describing a VPC.

## Example

    from cloudaux.orchestration.aws.vpc import get_vpc, FLAGS

    conn = dict(
        account_number='012345678910',
        assume_role='SecurityMonkey',
        region="us-west-2")

    queue = get_vpc('vpc-xxxxxxxx', flags=FLAGS.ALL, **conn)

    # The flags parameter is optional but allows the user to indicate that
    # only a subset of the full item description is required.
    # VPC Flag Options are:
    #   BASE, INTERNET_GATEWAY, CLASSIC_LINK, VPC_PEERING_CONNECTIONS, SUBNETS, ROUTE_TABLES,
    #   NETWORK_ACLS, FLOW_LOGS,  ALL (default)
    # For instance: flags=FLAGS.INTERNET_GATEWAY | FLAGS.VPC_PEERING_CONNECTIONS

    print(json.dumps(vpc, indent=2, sort_keys=True))

    {
        "Arn": "arn:aws:ec2:us-east-1:012345678910:vpc/vpc-xxxxxxxx",
        "Id": "vpc-xxxxxxxx",
        "Name": "MyVPC",
        "Region": "us-east-1",
        "Tags": [
            {
                "Key": "Name",
                "Value": "MyVPC"
            }
        ],
        "IsDefault": false,
        "InstanceTenancy": "default",
        "DhcpOptionsId": "dopt-xxxxxxxx",
        "CidrBlock": "10.0.0.0/16",
        "CidrBlockAssociationSet": [
            {
                "AssociationId": "vpc-cidr-assoc-xxxxxxxx",
                "CidrBlock": "10.0.0.0/16",
                "CidrBlockState": {
                    "State": "associated"
                }
            },
            {
                "AssociationId": "vpc-cidr-assoc-xxxxxxxy",
                "CidrBlock": "10.1.0.0/16",
                "CidrBlockState": {
                    "State": "associated"
                }
            }
        ],
        "Ipv6CidrBlockAssociationSet": [
            {
                "AssociationId": "vpc-cidr-assoc-xxxxxxxz",
                "Ipv6CidrBlock": "fde8:2d1a:7900:ea96::/64",
                "Ipv6CidrBlockState": {
                    "State": "associated"
                }
            }
        ],
        "Attributes": {
            "EnableDnsHostnames": {
                "Value": true
            },
            "EnableDnsSupport": {
                "Value": true
            }
        },
        "_version": 1,
        "FlowLogs": [
            "fl-xxxxxxxx",
            "fl-xxxxxxxy"
        ],
        "ClassicLink": {
            "Enabled": false,
            "DnsEnabled": false
        },
        "InternetGateway": {
            "State": "available",
            "Id": "igw-xxxxxxxx",
            "Tags": [
                {
                    "Key": "Name",
                    "Value": "MyInternetGateway"
                }
            ]
        },
        "VpcPeeringConnections": [
            "pcx-xxxxxxxx",
            "pcx-xxxxxxxy"
        ],
        "Subnets": [
            "subnet-xxxxxxxx",
            "subnet-xxxxxxxy"
        ],
        "RouteTables": [
            "rtb-xxxxxxxx",
            "rtb-xxxxxxxy"
        ],
        "NetworkAcls": [
            "acl-xxxxxxxx",
            "acl-xxxxxxxy"
        ]
    }

## Flags

The `get_vpc` command accepts flags describing what parts of the structure to build out.

If not provided, `get_vpc` assumes `FLAGS.ALL`.
