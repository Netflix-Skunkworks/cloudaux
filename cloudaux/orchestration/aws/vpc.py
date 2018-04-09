"""
.. module: cloudaux.orchestration.aws.vpc
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Mike Grima <mgrima@netflix.com>
"""
from botocore.exceptions import ClientError

from cloudaux.aws.ec2 import describe_vpcs, describe_dhcp_options, describe_vpc_classic_link, \
    describe_vpc_classic_link_dns_support, describe_internet_gateways, describe_vpc_peering_connections, \
    describe_subnets, describe_route_tables, describe_network_acls, describe_vpc_attribute, describe_flow_logs
from cloudaux.decorators import modify_output
from flagpole import FlagRegistry, Flags

from cloudaux.exceptions import CloudAuxException

registry = FlagRegistry()
FLAGS = Flags('BASE', 'INTERNET_GATEWAY', 'CLASSIC_LINK', 'VPC_PEERING_CONNECTIONS', 'SUBNETS', 'ROUTE_TABLES',
              'NETWORK_ACLS', 'FLOW_LOGS')


@registry.register(flag=FLAGS.FLOW_LOGS, depends_on=FLAGS.BASE, key="flow_logs")
def get_vpc_flow_logs(vpc, **conn):
    """Gets the VPC Flow Logs for a VPC"""
    fl_result = describe_flow_logs(Filters=[{"Name": "resource-id", "Values": [vpc["id"]]}], **conn)

    fl_ids = []
    for fl in fl_result:
        fl_ids.append(fl["FlowLogId"])

    return fl_ids


@registry.register(flag=FLAGS.CLASSIC_LINK, depends_on=FLAGS.BASE, key="classic_link")
def get_classic_link(vpc, **conn):
    """Gets the Classic Link details about a VPC"""
    result = {}

    try:
        cl_result = describe_vpc_classic_link(VpcIds=[vpc["id"]], **conn)[0]
        result["Enabled"] = cl_result["ClassicLinkEnabled"]

        # Check for DNS as well:
        dns_result = describe_vpc_classic_link_dns_support(VpcIds=[vpc["id"]], **conn)[0]
        result["DnsEnabled"] = dns_result["ClassicLinkDnsSupported"]
    except ClientError as e:
        # This is not supported for all regions.
        if 'UnsupportedOperation' not in str(e):
            raise e

    return result


@registry.register(flag=FLAGS.INTERNET_GATEWAY, depends_on=FLAGS.BASE, key="internet_gateway")
def get_internet_gateway(vpc, **conn):
    """Gets the Internet Gateway details about a VPC"""
    result = {}
    ig_result = describe_internet_gateways(Filters=[{"Name": "attachment.vpc-id", "Values": [vpc["id"]]}], **conn)

    if ig_result:
        # Only 1 IG can be attached to a VPC:
        result.update({
            "State": ig_result[0]["Attachments"][0]["State"],
            "Id": ig_result[0]["InternetGatewayId"],
            "Tags": ig_result[0].get("Tags", [])
        })

    return result


@registry.register(flag=FLAGS.VPC_PEERING_CONNECTIONS, depends_on=FLAGS.BASE, key="vpc_peering_connections")
def get_vpc_peering_connections(vpc, **conn):
    """Gets the Internet Gateway details about a VPC"""
    accepter_result = describe_vpc_peering_connections(Filters=[{"Name": "accepter-vpc-info.vpc-id",
                                                                 "Values": [vpc["id"]]}], **conn)

    requester_result = describe_vpc_peering_connections(Filters=[{"Name": "requester-vpc-info.vpc-id",
                                                                 "Values": [vpc["id"]]}], **conn)

    # Assuming that there will be no duplicates:
    peer_ids = []
    for peering in accepter_result + requester_result:
        peer_ids.append(peering["VpcPeeringConnectionId"])

    return peer_ids


@registry.register(flag=FLAGS.SUBNETS, depends_on=FLAGS.BASE, key="subnets")
def get_subnets(vpc, **conn):
    """Gets the VPC Subnets"""
    subnets = describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc["id"]]}], **conn)

    s_ids = []
    for s in subnets:
        s_ids.append(s["SubnetId"])

    return s_ids


@registry.register(flag=FLAGS.ROUTE_TABLES, depends_on=FLAGS.BASE, key="route_tables")
def get_route_tables(vpc, **conn):
    """Gets the VPC Route Tables"""
    route_tables = describe_route_tables(Filters=[{"Name": "vpc-id", "Values": [vpc["id"]]}], **conn)

    rt_ids = []
    for r in route_tables:
        rt_ids.append(r["RouteTableId"])

    return rt_ids


@registry.register(flag=FLAGS.NETWORK_ACLS, depends_on=FLAGS.BASE, key="network_acls")
def get_network_acls(vpc, **conn):
    """Gets the VPC Network ACLs"""
    route_tables = describe_network_acls(Filters=[{"Name": "vpc-id", "Values": [vpc["id"]]}], **conn)

    nacl_ids = []
    for r in route_tables:
        nacl_ids.append(r["NetworkAclId"])

    return nacl_ids


@registry.register(flag=FLAGS.BASE)
def get_base(vpc, **conn):
    """
    The base will return:
    - ARN
    - Region
    - Name
    - Id
    - Tags
    - IsDefault
    - InstanceTenancy
    - CidrBlock
    - CidrBlockAssociationSet
    - Ipv6CidrBlockAssociationSet
    - DhcpOptionsId
    - Attributes
    - _version

    :param bucket_name:
    :param conn:
    :return:
    """
    # Get the base:
    base_result = describe_vpcs(VpcIds=[vpc["id"]], **conn)[0]

    # The name of the VPC is in the tags:
    vpc_name = None
    for t in base_result.get("Tags", []):
        if t["Key"] == "Name":
            vpc_name = t["Value"]

    dhcp_opts = None
    # Get the DHCP Options:
    if base_result.get("DhcpOptionsId"):
        # There should only be exactly 1 attached to a VPC:
        dhcp_opts = describe_dhcp_options(DhcpOptionsIds=[base_result["DhcpOptionsId"]], **conn)[0]["DhcpOptionsId"]

    # Get the Attributes:
    attributes = {}
    attr_vals = [
        ("EnableDnsHostnames", "enableDnsHostnames"),
        ("EnableDnsSupport", "enableDnsSupport")
    ]
    for attr, query in attr_vals:
        attributes[attr] = describe_vpc_attribute(VpcId=vpc["id"], Attribute=query, **conn)[attr]

    vpc.update({
        'name': vpc_name,
        'region': conn["region"],
        'tags': base_result.get("Tags", []),
        'is_default': base_result["IsDefault"],
        'instance_tenancy': base_result["InstanceTenancy"],
        'dhcp_options_id': dhcp_opts,
        'cidr_block': base_result["CidrBlock"],
        'cidr_block_association_set': base_result.get("CidrBlockAssociationSet", []),
        'ipv6_cidr_block_association_set': base_result.get("Ipv6CidrBlockAssociationSet", []),
        'attributes': attributes,
        '_version': 1
    })
    return vpc


@modify_output
def get_vpc(vpc_id, flags=FLAGS.ALL, **conn):
    """
    Orchestrates all the calls required to fully fetch details about a VPC:

    {
        "Arn": ...,
        "Region": ...,
        "Name": ...,
        "Id": ...,
        "Tags: ...,
        "VpcPeeringConnections": ...,
        "ClassicLink": ...,
        "DhcpOptionsId": ...,
        "InternetGateway": ...,
        "IsDefault": ...,
        "CidrBlock": ...,
        "CidrBlockAssociationSet": ...,
        "Ipv6CidrBlockAssociationSet": ...,
        "InstanceTenancy": ...,
        "RouteTables": ...,
        "NetworkAcls": ...,
        "FlowLogs": ...,
        "Subnets": ...,
        "Attributes": ...,
        "FlowLogs": ...,
        "_version": 1
    }

    :param vpc_id: The ID of the VPC
    :param flags:
    :param conn:
    :return:
    """
    # Is the account number that's passed in the same as in the connection dictionary?
    if not conn.get("account_number"):
        raise CloudAuxException({"message": "Must supply account number in the connection dict to construct "
                                            "the VPC ARN.",
                                 "vpc_id": vpc_id})

    if not conn.get("region"):
        raise CloudAuxException({"message": "Must supply region in the connection dict to construct "
                                            "the VPC ARN.",
                                 "vpc_id": vpc_id})

    start = {
        'arn': "arn:aws:ec2:{region}:{account}:vpc/{vpc_id}".format(region=conn["region"],
                                                                    account=conn["account_number"],
                                                                    vpc_id=vpc_id),
        'id': vpc_id
    }

    return registry.build_out(flags, start_with=start, pass_datastructure=True, **conn)
