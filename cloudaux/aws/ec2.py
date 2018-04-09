"""
.. module: cloudaux.aws.ec2
    :platform: Unix
    :copyright: (c) 2015 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Mike Grima <mgrima@netflix.com>
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
.. moduleauthor:: Patrick Kelley <patrick@netflix.com>
"""
from cloudaux.aws.sts import sts_conn
from cloudaux.exceptions import CloudAuxException
from cloudaux.aws.decorators import rate_limited, paginated


@sts_conn('ec2')
@rate_limited()
def create_group(group, account_number=None, region=None, assume_role=None, client=None):
    if group.vpc_id:
        group_id = client.create_security_group(
                GroupName=group.name,
                Description=group.description,
                VpcId=group.vpc_id
        )['GroupId']
    else:
        group_id = client.create_security_group(
                GroupName=group.name,
                Description=group.description
        )['GroupId']

    return group_id


@sts_conn('ec2')
@rate_limited()
def delete_group(group, account_number=None, region=None, assume_role=None, client=None):
    client.delete_security_group(
            GroupId=group.aws_group_id
    )


@sts_conn('ec2')
@rate_limited()
def authorize_rule(rule, group, account_number=None, region=None, assume_role=None, client=None):
    if rule.direction == 'egress':
        # response = client.authorize_security_group_egress()
        raise CloudAuxException("Modifying egress rules is not yet supported.")
    else:
        if rule.cidr:
            client.authorize_security_group_ingress(
                    GroupId=group.aws_group_id,
                    IpProtocol=rule.protocol,
                    FromPort=rule.from_port,
                    ToPort=rule.to_port,
                    CidrIp=rule.cidr
            )
        else:
            client.authorize_security_group_ingress(
                    GroupId=group.aws_group_id,
                    IpProtocol=rule.protocol,
                    FromPort=rule.from_port,
                    ToPort=rule.to_port,
                    SourceSecurityGroupName=rule.source_security_group.name,
                    # SourceSecurityGroupOwnerId=rule.source_security_group.account.aws_account_id
            )


@sts_conn('ec2')
@rate_limited()
def revoke_rule(rule, group, account_number=None, region=None, assume_role=None, client=None):
    if rule.direction == 'egress':
        # response = client.authorize_security_group_egress()
        raise CloudAuxException("Modifying egress rules is not yet supported.")
    else:
        client.revoke_security_group_ingress(
                GroupId=group.aws_group_id,
                IpProtocol=rule.protocol,
                FromPort=rule.from_port,
                ToPort=rule.to_port,
                CidrIp=rule.cidr,
        )


@sts_conn('ec2')
@rate_limited()
def add_groups_to_instance(instance_id, groups, account_number=None, region=None, assume_role=None, client=None):
    client.modify_instance_attribute(InstanceId=instance_id, Groups=groups)


@sts_conn('ec2')
@rate_limited()
def describe_instances(**kwargs):
    return kwargs.pop('client').get_paginator('describe_instances').paginate()


@sts_conn('ec2')
@rate_limited()
def describe_vpn_connections(**kwargs):
    return kwargs.pop('client').describe_vpn_connections(**kwargs).get("VpnConnections", [])


@sts_conn('ec2')
@rate_limited()
def describe_images(**kwargs):
    return kwargs.pop('client').describe_images(**kwargs)['Images']


@sts_conn('ec2')
@rate_limited()
def describe_image_attribute(**kwargs):
    return kwargs.pop('client').describe_image_attribute(**kwargs)


@sts_conn('ec2')
@rate_limited()
def describe_security_groups(**kwargs):
    return kwargs.pop('client').describe_security_groups(**kwargs)


@sts_conn('ec2')
@rate_limited()
def create_security_group(**kwargs):
    return kwargs.pop('client').create_security_group(**kwargs)


@sts_conn('ec2')
@rate_limited()
def authorize_security_group_ingress(**kwargs):
    return kwargs.pop('client').authorize_security_group_ingress(**kwargs)


@sts_conn('ec2')
@rate_limited()
def authorize_security_group_egress(**kwargs):
    return kwargs.pop('client').authorize_security_group_egress(**kwargs)


@sts_conn('ec2')
@rate_limited()
def describe_auto_scaling_groups(**kwargs):
    return kwargs.pop('client').describe_auto_scaling_groups(**kwargs)


# ------------------ #
# VPC is part of EC2 #
# ------------------ #
@sts_conn('ec2')
@rate_limited()
def describe_vpcs(**kwargs):
    return kwargs.pop('client').describe_vpcs(**kwargs).get("Vpcs", [])


@sts_conn('ec2')
@rate_limited()
def describe_dhcp_options(**kwargs):
    return kwargs.pop('client').describe_dhcp_options(**kwargs).get("DhcpOptions", [])


@sts_conn('ec2')
@rate_limited()
def describe_internet_gateways(**kwargs):
    return kwargs.pop('client').describe_internet_gateways(**kwargs).get("InternetGateways", [])


@sts_conn('ec2')
@rate_limited()
def describe_vpc_classic_link(**kwargs):
    return kwargs.pop('client').describe_vpc_classic_link(**kwargs).get("Vpcs", [])


@paginated('Vpcs', response_pagination_marker='NextToken')
@sts_conn('ec2')
@rate_limited()
def describe_vpc_classic_link_dns_support(**kwargs):
    return kwargs.pop('client').describe_vpc_classic_link_dns_support(**kwargs)


@sts_conn('ec2')
@rate_limited()
def describe_vpc_peering_connections(**kwargs):
    return kwargs.pop('client').describe_vpc_peering_connections(**kwargs).get("VpcPeeringConnections", [])


@sts_conn('ec2')
@rate_limited()
def describe_subnets(**kwargs):
    return kwargs.pop('client').describe_subnets(**kwargs).get("Subnets", [])


@sts_conn('ec2')
@rate_limited()
def describe_route_tables(**kwargs):
    return kwargs.pop('client').describe_route_tables(**kwargs).get("RouteTables", [])


@sts_conn('ec2')
@rate_limited()
def describe_network_acls(**kwargs):
    return kwargs.pop('client').describe_network_acls(**kwargs).get("NetworkAcls", [])


@sts_conn('ec2')
@rate_limited()
def describe_vpc_attribute(**kwargs):
    return kwargs.pop('client').describe_vpc_attribute(**kwargs)


@sts_conn('ec2')
@rate_limited()
def describe_flow_logs(**kwargs):
    return kwargs.pop('client').describe_flow_logs(**kwargs).get("FlowLogs", [])
# ------------------ #

