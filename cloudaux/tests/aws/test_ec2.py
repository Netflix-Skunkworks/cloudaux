"""
.. module: cloudaux.tests.aws.test_ec2
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Mike Grima <mgrima@netflix.com>
"""

from cloudaux.aws.ec2 import describe_vpcs, describe_dhcp_options, describe_internet_gateways, \
    describe_vpc_peering_connections, describe_subnets, describe_route_tables, describe_network_acls, \
    describe_vpc_attribute


def test_describe_vpcs(test_vpc):
    result = describe_vpcs()

    assert len(result) == 2

    # Find the non-default VPC and do stuff:
    for v in result:
        if v["CidrBlock"] == '172.31.0.0/16':
            assert v["IsDefault"]

        else:
            vpc_cidrs = ["10.0.0.0/16", "10.1.0.0/16"]
            assert v["CidrBlock"] == "10.0.0.0/16"
            assert v["InstanceTenancy"] == "default"
            assert len(v["Tags"]) == 2
            assert not v["IsDefault"]
            assert len(v["CidrBlockAssociationSet"]) == 2
            vpc_cidrs.remove(v["CidrBlockAssociationSet"][0]["CidrBlock"])
            vpc_cidrs.remove(v["CidrBlockAssociationSet"][1]["CidrBlock"])
            assert not vpc_cidrs
            assert len(v["Ipv6CidrBlockAssociationSet"]) == 1
            assert v["Ipv6CidrBlockAssociationSet"][0]["Ipv6CidrBlock"] == "fde8:2d1a:7900:ea96::/64"


def test_describe_dhcp_options(test_vpc, dhcp_options):
    result = describe_dhcp_options(DhcpOptionsIds=[dhcp_options["DhcpOptionsId"]])

    assert len(result) == 1
    assert result[0]["DhcpConfigurations"][0]["Key"] == 'domain-name-servers'
    assert len(result[0]["DhcpConfigurations"][0]["Values"]) == 2

    test_vpc = describe_vpcs(VpcIds=[test_vpc["VpcId"]])
    assert test_vpc[0]["DhcpOptionsId"] == result[0]["DhcpOptionsId"]


def test_describe_internet_gateways(test_vpc, internet_gateway_vpc):
    result = describe_internet_gateways(InternetGatewayIds=[internet_gateway_vpc["InternetGatewayId"]])

    assert len(result) == 1
    assert len(result[0]["Attachments"]) == 1
    assert result[0]["Attachments"][0]["State"] == 'available'
    assert result[0]["Attachments"][0]["VpcId"] == test_vpc["VpcId"]
    assert result[0]["InternetGatewayId"] == internet_gateway_vpc["InternetGatewayId"]

    # Try with a filter:
    result = describe_internet_gateways(Filters=[{"Name": "attachment.vpc-id", "Values": [test_vpc["VpcId"]]}])
    assert len(result) == 1
    assert result[0]["Attachments"][0]["VpcId"] == test_vpc["VpcId"]


def test_describe_vpc_peering_connections(test_vpc, vpc_peering_connection):
    result = describe_vpc_peering_connections(VpcPeeringConnectionIds=
                                              [vpc_peering_connection["VpcPeeringConnectionId"]])

    assert len(result) == 1
    assert result[0]["RequesterVpcInfo"]["CidrBlock"] == "10.0.0.0/16"
    assert result[0]["RequesterVpcInfo"]["VpcId"] == test_vpc["VpcId"]


def test_describe_subnets(test_vpc, subnet):
    result = describe_subnets(SubnetIds=[subnet["SubnetId"]])

    assert len(result) == 1
    assert result[0]["CidrBlock"] == "10.0.0.0/16"
    assert result[0]["SubnetId"] == subnet["SubnetId"]
    assert result[0]["VpcId"] == test_vpc["VpcId"]

    # Try with a filter:
    result = describe_subnets(Filters=[{"Name": "vpc-id", "Values": [test_vpc["VpcId"]]}])
    assert len(result) == 1
    assert result[0]["VpcId"] == test_vpc["VpcId"]
    assert result[0]["SubnetId"] == subnet["SubnetId"]


def test_describe_route_tables(test_vpc, route_table):
    result = describe_route_tables(RouteTableIds=[route_table["RouteTableId"]])

    assert len(result) == 1
    assert result[0]["RouteTableId"] == route_table["RouteTableId"]
    assert result[0]["VpcId"] == test_vpc["VpcId"]

    # Try with a filter:
    result = describe_route_tables(Filters=[{"Name": "vpc-id", "Values": [test_vpc["VpcId"]]}])
    # Moto returns 2:
    found = False
    for r in result:
        assert r["VpcId"] == test_vpc["VpcId"]
        if r["RouteTableId"] == route_table["RouteTableId"]:
            found = True

    assert found


def test_describe_network_acls(test_vpc, network_acl):
    result = describe_network_acls(NetworkAclIds=[network_acl["NetworkAclId"]])

    assert len(result) == 1
    assert result[0]["NetworkAclId"] == network_acl["NetworkAclId"]
    assert result[0]["VpcId"] == test_vpc["VpcId"]

    # Try with a filter:
    result = describe_network_acls(Filters=[{"Name": "vpc-id", "Values": [test_vpc["VpcId"]]}])
    # Moto returns 2:
    found = False
    for r in result:
        assert r["VpcId"] == test_vpc["VpcId"]
        if r["NetworkAclId"] == network_acl["NetworkAclId"]:
            found = True

    assert found


def test_describe_vpc_attribute(test_vpc):
    result = describe_vpc_attribute(VpcId=test_vpc["VpcId"], Attribute="enableDnsSupport")
    assert result["EnableDnsSupport"]
    result = describe_vpc_attribute(VpcId=test_vpc["VpcId"], Attribute="enableDnsHostnames")
    assert result["EnableDnsHostnames"]
