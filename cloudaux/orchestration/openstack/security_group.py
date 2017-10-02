"""
.. module: cloudaux.openstack.orchestration.security_group
    :platform: Unix
    :copyright: Copyright (c) 2017 AT&T Intellectual Property. All rights reserved. See AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Michael Stair <mstair@att.com>
"""
from cloudaux.openstack.utils import list_items
from flagpole import FlagRegistry, Flags

registry = FlagRegistry()
FLAGS = Flags('RULES','INSTANCES')


@registry.register(flag=FLAGS.INSTANCES, depends_on=FLAGS.RULES, key='assigned_to')
def get_instances(security_group, **kwargs):
    detail = kwargs.pop('instance_detail', 'FULL')

    kwargs['service'] = 'compute'
    kwargs['generator'] = 'servers'
    instances = list_items(**kwargs)

    sg_instances = {}
    for instance in instances:
        for group in instance.security_groups:
            if group['name'] not in sg_instances:
                sg_instances[group['name']] = [instance]
            else:
                sg_instances[group['name']].append(instance)
    if detail == 'SUMMARY':
        if security_group['name'] in sg_instances:
            assigned_to = "{} instances".format(len(sg_instances[security_group['name']]))
        else:
            assigned_to = "0 instances"
    elif detail == 'FULL':
        assigned_to = []
        if security_group['name'] in sg_instances:
            for instance in sg_instances[security_group['name']]:
                tagdict = {"instance_id": instance.id}
                assigned_to.append(tagdict)
    return assigned_to

@registry.register(flag=FLAGS.RULES)
def get_rules(security_group, **kwargs):
    """ format the rule fields to match AWS to support auditor reuse,
        will need to remap back if we want to orchestrate from our stored items """
    rules = security_group.pop('security_group_rules',[])
    for rule in rules:
        rule['ip_protocol'] = rule.pop('protocol')
        rule['from_port'] = rule.pop('port_range_max')
        rule['to_port'] = rule.pop('port_range_min')
        rule['cidr_ip'] = rule.pop('remote_ip_prefix')
        rule['rule_type'] = rule.pop('direction')
    security_group['rules'] = sorted(rules)
    return security_group

def get_security_group(security_group, flags=FLAGS.ALL, **kwargs):
    result = registry.build_out(flags, start_with=security_group,  pass_datastructure=True, **kwargs)
    """ just store the AWS formatted rules """
    result.pop('security_group_rules', [])
    return result
