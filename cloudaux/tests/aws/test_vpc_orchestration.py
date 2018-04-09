"""
.. module: cloudaux.tests.aws.test_vpc_orchestration
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Mike Grima <mgrima@netflix.com>
"""
import pytest
from botocore.exceptions import ClientError

from cloudaux.exceptions import CloudAuxException


def perform_base_tests(test_vpc, dhcp_options, result):
    assert result["Arn"] == "arn:aws:ec2:us-east-1:012345678912:vpc/{}".format(test_vpc["VpcId"])
    assert result["Name"] == "myvpc"
    assert result["Id"] == test_vpc["VpcId"]
    assert len(result["Tags"]) == 2
    assert result["Region"] == "us-east-1"
    assert not result["IsDefault"]
    assert result["InstanceTenancy"] == "default"
    assert result["DhcpOptionsId"] == dhcp_options["DhcpOptionsId"]
    assert result["CidrBlock"] == "10.0.0.0/16"
    assert len(result["CidrBlockAssociationSet"]) == 2
    assert len(result["Ipv6CidrBlockAssociationSet"]) == 1
    assert result["Attributes"]["EnableDnsHostnames"]
    assert result["Attributes"]["EnableDnsSupport"]
    assert result["_version"] == 1


def test_get_base(ec2, test_vpc, dhcp_options):
    from cloudaux.orchestration.aws.vpc import get_vpc, FLAGS

    result = get_vpc(test_vpc["VpcId"], flags=FLAGS.BASE, account_number="012345678912", region="us-east-1")
    perform_base_tests(test_vpc, dhcp_options, result)

    # And without tags:
    ec2.delete_tags(Resources=[test_vpc["VpcId"]], Tags=[{"Key": "Name", "Value": "myvpc"}])
    result = get_vpc(test_vpc["VpcId"], flags=FLAGS.BASE, account_number="012345678912", region="us-east-1")
    assert len(result["Tags"]) == 1
    assert not result["Name"]


def test_get_base_errors():
    from cloudaux.orchestration.aws.vpc import get_vpc

    # No Account Number:
    with pytest.raises(CloudAuxException) as cae:
        get_vpc("vpc-012345678")

    assert "account number" in cae.value.args[0]["message"]
    assert cae.value.args[0]["vpc_id"] == "vpc-012345678"

    # No Region:
    with pytest.raises(CloudAuxException) as cae:
        get_vpc("vpc-012345678", account_number="012345678912")

    assert "region" in cae.value.args[0]["message"]
    assert cae.value.args[0]["vpc_id"] == "vpc-012345678"


def test_get_classic_link(test_vpc, dhcp_options, mock_classic_link):
    from cloudaux.orchestration.aws.vpc import get_vpc, get_classic_link, FLAGS

    result = get_classic_link({"id": test_vpc["VpcId"]}, force_client=mock_classic_link)
    assert result["Enabled"]
    assert result["DnsEnabled"]

    # With BASE:
    result = get_vpc(test_vpc["VpcId"], flags=FLAGS.CLASSIC_LINK, account_number="012345678912", region="us-east-1",
                     force_client=mock_classic_link)

    assert result["ClassicLink"]["Enabled"]
    assert result["ClassicLink"]["DnsEnabled"]
    perform_base_tests(test_vpc, dhcp_options, result)


def test_get_vpc_flow_logs(test_vpc, dhcp_options, mock_vpc_flow_logs):
    from cloudaux.orchestration.aws.vpc import get_vpc, get_vpc_flow_logs, FLAGS

    result = get_vpc_flow_logs({"id": test_vpc["VpcId"]}, force_client=mock_vpc_flow_logs)
    assert len(result) == 1
    assert result[0] == "fl-xxxxxxxx"

    # With BASE:
    result = get_vpc(test_vpc["VpcId"], flags=FLAGS.FLOW_LOGS, account_number="012345678912", region="us-east-1",
                     force_client=mock_vpc_flow_logs)

    assert len(result["FlowLogs"]) == 1
    assert result["FlowLogs"][0] == "fl-xxxxxxxx"
    perform_base_tests(test_vpc, dhcp_options, result)


def test_classic_link_exception(test_vpc, dhcp_options, mock_classic_link):
    from cloudaux.orchestration.aws.vpc import get_vpc, get_classic_link, FLAGS

    # Return an unsupported operation exception:
    def raise_exception(**kwargs):
        raise ClientError({"Error": {"Code": "UnsupportedOperation"}}, "DescribeVpcClassicLink")
    mock_classic_link.describe_vpc_classic_link = raise_exception

    result = get_classic_link({"id": test_vpc["VpcId"]}, force_client=mock_classic_link)
    assert not result

    # With BASE:
    result = get_vpc(test_vpc["VpcId"], flags=FLAGS.CLASSIC_LINK, account_number="012345678912", region="us-east-1",
                     force_client=mock_classic_link)

    assert not result["ClassicLink"]
    perform_base_tests(test_vpc, dhcp_options, result)


def test_get_internet_gateway_no_ig(test_vpc, dhcp_options):
    # Can't parametrize fixtures :(
    from cloudaux.orchestration.aws.vpc import get_vpc, get_internet_gateway, FLAGS

    result = get_internet_gateway({"id": test_vpc["VpcId"]})
    assert not result

    # With BASE:
    result = get_vpc(test_vpc["VpcId"], flags=FLAGS.INTERNET_GATEWAY, account_number="012345678912", region="us-east-1")
    assert not result["InternetGateway"]
    perform_base_tests(test_vpc, dhcp_options, result)


def test_get_internet_gateway(test_vpc, internet_gateway_vpc, dhcp_options):
    # Can't parametrize fixtures :(
    from cloudaux.orchestration.aws.vpc import get_vpc, get_internet_gateway, FLAGS

    result = get_internet_gateway({"id": test_vpc["VpcId"]})
    assert result["State"] == "available"
    assert result["Id"] == internet_gateway_vpc["InternetGatewayId"]
    assert not result["Tags"]

    # With BASE:
    result = get_vpc(test_vpc["VpcId"], flags=FLAGS.INTERNET_GATEWAY, account_number="012345678912", region="us-east-1")
    assert result["InternetGateway"]["State"] == "available"
    assert result["InternetGateway"]["Id"] == internet_gateway_vpc["InternetGatewayId"]
    assert not result["InternetGateway"]["Tags"]
    perform_base_tests(test_vpc, dhcp_options, result)


def test_get_vpc_peering_connections_no_connections(test_vpc, dhcp_options):
    from cloudaux.orchestration.aws.vpc import get_vpc, get_vpc_peering_connections, FLAGS

    result = get_vpc_peering_connections({"id": test_vpc["VpcId"]})
    assert not result

    # With BASE:
    result = get_vpc(test_vpc["VpcId"], flags=FLAGS.VPC_PEERING_CONNECTIONS, account_number="012345678912",
                     region="us-east-1")
    assert not result["VpcPeeringConnections"]
    perform_base_tests(test_vpc, dhcp_options, result)


def test_get_vpc_peering_connections(test_vpc, dhcp_options, vpc_peering_connection):
    from cloudaux.orchestration.aws.vpc import get_vpc, get_vpc_peering_connections, FLAGS

    result = get_vpc_peering_connections({"id": test_vpc["VpcId"]})

    # Moto improperly returns a duplicate -- this should be 1.
    assert result[0] == vpc_peering_connection["VpcPeeringConnectionId"]

    # With BASE:
    result = get_vpc(test_vpc["VpcId"], flags=FLAGS.VPC_PEERING_CONNECTIONS, account_number="012345678912",
                     region="us-east-1")
    assert result["VpcPeeringConnections"][0] == \
        vpc_peering_connection["VpcPeeringConnectionId"]
    perform_base_tests(test_vpc, dhcp_options, result)


def test_get_subnets_no_subnet(test_vpc, dhcp_options):
    from cloudaux.orchestration.aws.vpc import get_vpc, get_subnets, FLAGS

    result = get_subnets({"id": test_vpc["VpcId"]})
    assert not result

    # With BASE:
    result = get_vpc(test_vpc["VpcId"], flags=FLAGS.SUBNETS, account_number="012345678912", region="us-east-1")
    assert not result["Subnets"]
    perform_base_tests(test_vpc, dhcp_options, result)


def test_get_subnets(test_vpc, dhcp_options, subnet):
    from cloudaux.orchestration.aws.vpc import get_vpc, get_subnets, FLAGS

    result = get_subnets({"id": test_vpc["VpcId"]})
    assert len(result) == 1
    assert result[0] == subnet["SubnetId"]

    # With BASE:
    result = get_vpc(test_vpc["VpcId"], flags=FLAGS.SUBNETS, account_number="012345678912", region="us-east-1")
    assert len(result["Subnets"]) == 1
    assert result["Subnets"][0] == subnet["SubnetId"]
    perform_base_tests(test_vpc, dhcp_options, result)


def test_get_route_tables(test_vpc, dhcp_options, route_table):
    from cloudaux.orchestration.aws.vpc import get_vpc, get_route_tables, FLAGS

    # Moto always returns a default:
    result = get_route_tables({"id": test_vpc["VpcId"]})
    assert len(result) == 2
    found = False
    for r in result:
        if r == route_table["RouteTableId"]:
            found = True
    assert found

    # With BASE:
    result = get_vpc(test_vpc["VpcId"], flags=FLAGS.ROUTE_TABLES, account_number="012345678912", region="us-east-1")
    assert len(result["RouteTables"]) == 2
    found = False
    for r in result["RouteTables"]:
        if r == route_table["RouteTableId"]:
            found = True
    assert found
    perform_base_tests(test_vpc, dhcp_options, result)


def test_get_network_acls(test_vpc, dhcp_options, network_acl):
    from cloudaux.orchestration.aws.vpc import get_vpc, get_network_acls, FLAGS

    # Moto always returns a default:
    result = get_network_acls({"id": test_vpc["VpcId"]})
    assert len(result) == 2
    found = False
    for r in result:
        if r == network_acl["NetworkAclId"]:
            found = True
    assert found

    # With BASE:
    result = get_vpc(test_vpc["VpcId"], flags=FLAGS.NETWORK_ACLS, account_number="012345678912", region="us-east-1")
    assert len(result["NetworkAcls"]) == 2
    found = False
    for r in result["NetworkAcls"]:
        if r == network_acl["NetworkAclId"]:
            found = True
    assert found
    perform_base_tests(test_vpc, dhcp_options, result)
