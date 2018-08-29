"""
.. module: cloudaux.tests.aws.conftest
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Mike Grima <mgrima@netflix.com>
"""
from datetime import datetime
import json

import pytest

from moto import mock_ec2, mock_iam, mock_sts
import boto3

from cloudaux.aws.sts import boto3_cached_conn


@pytest.fixture(scope="function")
def conn_dict():
    return {
        "region": "us-east-1"
    }


@pytest.fixture(scope="function")
def sts(conn_dict):
    with mock_sts():
        yield boto3.client("sts", region_name="us-east-1")


@pytest.fixture(scope="function")
def ec2(sts, conn_dict):
    with mock_ec2():
        yield boto3_cached_conn("ec2", **conn_dict)


@pytest.fixture(scope="function")
def iam(sts, conn_dict):
    with mock_iam():
        yield boto3_cached_conn("iam", **conn_dict)


@pytest.fixture(scope="function")
def test_vpc(ec2):
    """Creates a test VPC"""
    vpc_id = ec2.create_vpc(CidrBlock="10.0.0.0/16")["Vpc"]["VpcId"]

    # Add More CIDRs:
    ec2.associate_vpc_cidr_block(CidrBlock="10.1.0.0/16", VpcId=vpc_id)
    ec2.associate_vpc_cidr_block(CidrBlock="fde8:2d1a:7900:ea96::/64", VpcId=vpc_id)

    # Add some tags:
    ec2.create_tags(Resources=[vpc_id], Tags=[{"Key": "TheVpc", "Value": vpc_id}, {"Key": "Name", "Value": "myvpc"}])

    vpc = ec2.describe_vpcs(VpcIds=[vpc_id])["Vpcs"][0]

    return vpc


@pytest.fixture(scope="function")
def dhcp_options(ec2, test_vpc):
    # DHCP Options:
    options_id = ec2.create_dhcp_options(DhcpConfigurations=[
        {
            "Key": "domain-name-servers",
            "Values": [
                '10.0.5.1',
                '10.0.5.2',
            ]
        }
    ])["DhcpOptions"]["DhcpOptionsId"]
    ec2.associate_dhcp_options(DhcpOptionsId=options_id, VpcId=test_vpc["VpcId"])

    return ec2.describe_dhcp_options(DhcpOptionsIds=[options_id])["DhcpOptions"][0]


@pytest.fixture(scope="function")
def internet_gateway_vpc(ec2, test_vpc):
    # Internet Gateway:
    gateway_id = ec2.create_internet_gateway()["InternetGateway"]["InternetGatewayId"]
    ec2.attach_internet_gateway(InternetGatewayId=gateway_id, VpcId=test_vpc["VpcId"])

    return ec2.describe_internet_gateways(InternetGatewayIds=[gateway_id])["InternetGateways"][0]


@pytest.fixture(scope="function")
def vpc_peering_connection(ec2, test_vpc):
    result = ec2.describe_vpcs()

    for v in result["Vpcs"]:
        if v["IsDefault"]:
            break

    # VPC Peering connection (with the default VPC)
    peering_id = ec2.create_vpc_peering_connection(
        PeerOwnerId="123456789012",
        PeerVpcId=v["VpcId"],
        VpcId=test_vpc["VpcId"],
        PeerRegion="us-east-1"
    )["VpcPeeringConnection"]["VpcPeeringConnectionId"]

    return ec2.describe_vpc_peering_connections(VpcPeeringConnectionIds=[peering_id])["VpcPeeringConnections"][0]


@pytest.fixture(scope="function")
def subnet(ec2, test_vpc):
    # Subnet
    subnet_id = ec2.create_subnet(CidrBlock="10.0.0.0/16", VpcId=test_vpc["VpcId"])["Subnet"]["SubnetId"]

    return ec2.describe_subnets(SubnetIds=[subnet_id])["Subnets"][0]


@pytest.fixture(scope="function")
def route_table(ec2, test_vpc, subnet):
    # Route Table
    rt_id = ec2.create_route_table(VpcId=test_vpc["VpcId"])["RouteTable"]["RouteTableId"]
    ec2.associate_route_table(RouteTableId=rt_id, SubnetId=subnet["SubnetId"])

    return ec2.describe_route_tables(RouteTableIds=[rt_id])["RouteTables"][0]


@pytest.fixture(scope="function")
def network_acl(ec2, test_vpc):
    # Network ACL
    nacl_id = ec2.create_network_acl(VpcId=test_vpc["VpcId"])["NetworkAcl"]["NetworkAclId"]

    return ec2.describe_network_acls(NetworkAclIds=[nacl_id])["NetworkAcls"][0]


@pytest.fixture(scope="function")
def mock_vpc_flow_logs(ec2, test_vpc):
    # VPC Flow Logs
    conn = boto3_cached_conn(
        "ec2",
        service_type="client",
        future_expiration_minutes=15,
        account_number="012345678912",
        region='us-east-1')

    def describe_flow_logs(**kwargs):
        """
        # Too lazy to submit a PR to Moto -- Probably worth the trouble.
        :param kwargs:
        :return:
        """
        return {
            "FlowLogs": [
                {
                    "CreationTime": datetime(2018, 4, 1),
                    "DeliverLogsPermissionArn": "arn:aws:iam::012345678912:role/FlowLogRole",
                    "FlowLogId": "fl-xxxxxxxx",
                    "FlowLogStatus": "ACTIVE",
                    "LogGroupName": "TheLogGroup",
                    "ResourceId": test_vpc["VpcId"],
                    "TrafficType": "ALL"
                }
            ]
        }

    setattr(conn, "describe_flow_logs", describe_flow_logs)

    return conn


@pytest.fixture(scope="function")
def mock_classic_link(ec2):
    conn = boto3_cached_conn(
        "ec2",
        service_type="client",
        future_expiration_minutes=15,
        account_number="012345678912",
        region='us-east-1')

    def describe_vpc_classic_link(**kwargs):
        """
        # Too lazy to submit a PR to Moto -- not worth the trouble for ClassicLink
        :param kwargs:
        :return:
        """
        return {
            "Vpcs": [
                {
                    "ClassicLinkEnabled": True,
                    "Tags": [],
                    "VpcId": kwargs["VpcIds"][0]
                }
            ]
        }

    def describe_vpc_classic_link_dns_support(**kwargs):
        """
        # Too lazy to submit a PR to Moto -- not worth the trouble for ClassicLink
        :param kwargs:
        :return:
        """
        return {
            "Vpcs": [
                {
                    "ClassicLinkDnsSupported": True,
                    "VpcId": kwargs["VpcIds"][0]
                }
            ]
        }

    setattr(conn, "describe_vpc_classic_link", describe_vpc_classic_link)
    setattr(conn, "describe_vpc_classic_link_dns_support", describe_vpc_classic_link_dns_support)

    return conn


@pytest.fixture(scope="function")
def test_iam(iam):
    """Creates and setups up IAM things"""

    role = iam.create_role(
        Path='/',
        RoleName='testRoleCloudAuxName',
        AssumeRolePolicyDocument=json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "ec2.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }),
        Description='Test Description'
    )

    user = iam.create_user(
        Path='/',
        UserName='testCloudAuxUser'
    )


    group = iam.create_group(
        Path='/',
        GroupName='testCloudAuxGroup'
    )

    policy = iam.create_policy(
        PolicyName='testCloudAuxPolicy',
        Path='/',
        PolicyDocument=json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "s3:ListBucket",
                    "Resource": "*",
                    "Effect": "Allow",
                }
            ]
        }),
        Description='Test CloudAux Policy'
    )

    return iam
