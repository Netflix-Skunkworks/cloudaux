"""
.. module: cloudaux.tests.aws.conftest
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Mike Grima <mgrima@netflix.com>
"""
import os
from datetime import datetime
import json

import pytest

from moto import mock_ec2, mock_iam, mock_sts
import boto3

from cloudaux.aws.sts import boto3_cached_conn


MOCK_CERT_ONE = """-----BEGIN CERTIFICATE-----
MIIBpzCCARACCQCY5yOdxCTrGjANBgkqhkiG9w0BAQsFADAXMRUwEwYDVQQKDAxt
b3RvIHRlc3RpbmcwIBcNMTgxMTA1MTkwNTIwWhgPMjI5MjA4MTkxOTA1MjBaMBcx
FTATBgNVBAoMDG1vdG8gdGVzdGluZzCBnzANBgkqhkiG9w0BAQEFAAOBjQAwgYkC
gYEA1Jn3g2h7LD3FLqdpcYNbFXCS4V4eDpuTCje9vKFcC3pi/01147X3zdfPy8Mt
ZhKxcREOwm4NXykh23P9KW7fBovpNwnbYsbPqj8Hf1ZaClrgku1arTVhEnKjx8zO
vaR/bVLCss4uE0E0VM1tJn/QGQsfthFsjuHtwx8uIWz35tUCAwEAATANBgkqhkiG
9w0BAQsFAAOBgQBWdOQ7bDc2nWkUhFjZoNIZrqjyNdjlMUndpwREVD7FQ/DuxJMj
FyDHrtlrS80dPUQWNYHw++oACDpWO01LGLPPrGmuO/7cOdojPEd852q5gd+7W9xt
8vUH+pBa6IBLbvBp+szli51V3TLSWcoyy4ceJNQU2vCkTLoFdS0RLd/7tQ==
-----END CERTIFICATE-----"""


MOCK_CERT_TWO = """-----BEGIN CERTIFICATE-----
MIIBrzCCARgCCQCICxdQxUUR4TANBgkqhkiG9w0BAQsFADAbMRkwFwYDVQQLDBBD
bG91ZEF1eCBUZXN0aW5nMCAXDTE4MTEwNTIyNDgwMVoYDzIyOTIwODE5MjI0ODAx
WjAbMRkwFwYDVQQLDBBDbG91ZEF1eCBUZXN0aW5nMIGfMA0GCSqGSIb3DQEBAQUA
A4GNADCBiQKBgQCz16wzxaVPKRYr+ibVIFBfuEBqEDkIwx6EP9nwu+PZ4AHClRpa
TmVvhE90W55B5aGY///EIpkaowMBWO19iP2INUTUrHfQ9/ZwHFyq3htsN4Idb8vM
EMu/abBOyCDi5vIAwx81AglUrGFiLQ+qNPY/idlDo1Q3l2V7Z7aGlAY5jwIDAQAB
MA0GCSqGSIb3DQEBCwUAA4GBAHLJkvkcvIYZZYHI7LaUU8meuNa1HAQJnj/MB8LK
oDoWCLmjx8oBH4XUzlupA087q6j1PQWyu1lm7j3lTze0j//XXlrwOXHL1z3QZ5Ys
jRnIubUjNlVDBTuG/B6GWdxQiELscHsXezmXOxtiuHeB30VEf+/GzJw4gGXV+Rwc
bKw4
-----END CERTIFICATE-----"""


@pytest.fixture(scope="function")
def conn_dict():
    return {
        "region": "us-east-1"
    }


@pytest.fixture(scope='function')
def aws_credentials():
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'


@pytest.fixture(scope="function")
def sts(aws_credentials, conn_dict):
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


@pytest.fixture(scope='function')
def mock_iam_client(iam):
    yield boto3_cached_conn(
        'iam',
        service_type='client',
        future_expiration_minutes=15,
        account_number='123456789012',
        region='us-east-1')


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
    # Role
    iam.create_role(
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

    # Instance Profile:
    iam.create_instance_profile(InstanceProfileName='testIPCloudAuxName')
    iam.add_role_to_instance_profile(InstanceProfileName='testIPCloudAuxName', RoleName='testRoleCloudAuxName')

    # User
    iam.create_user(
        Path='/',
        UserName='testCloudAuxUser'
    )

    # Group
    iam.create_group(
        Path='/',
        GroupName='testCloudAuxGroup'
    )

    # Policy
    iam.create_policy(
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


@pytest.fixture(scope='function')
def group_fixture(test_iam):
    """Fixture to add complexity to the IAM group.

    This will associate:
    - an IAM user to the group
    - an IAM managed policy to the group
    """
    # Associate the group to a user:
    test_iam.add_user_to_group(GroupName='testCloudAuxGroup', UserName='testCloudAuxUser')

    # Associate a managed policy to the group:
    test_iam.attach_group_policy(GroupName='testCloudAuxGroup',
                                 PolicyArn='arn:aws:iam::123456789012:policy/testCloudAuxPolicy')

    # Add an inline policy to the group:
    test_iam.put_group_policy(GroupName='testCloudAuxGroup', PolicyName='TestPolicy',
                              PolicyDocument=json.dumps({
                                  "Version": "2012-10-17",
                                  "Statement": [
                                      {
                                          "Action": "s3:ListBucket",
                                          "Resource": "*",
                                          "Effect": "Allow",
                                      }
                                  ]
                              }))

    yield test_iam


@pytest.fixture(scope='function')
def server_certificates(iam):
    """Fixture that creates 2 IAM SSL certs."""
    iam.upload_server_certificate(
        ServerCertificateName='certOne',
        CertificateBody=MOCK_CERT_ONE,
        PrivateKey='SomePrivateKey'
    )

    iam.upload_server_certificate(
        ServerCertificateName='certTwo',
        CertificateBody=MOCK_CERT_TWO,
        PrivateKey='SomeOtherPrivateKey'
    )

    yield iam
