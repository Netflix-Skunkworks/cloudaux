"""
.. module: cloudaux.orchestration.aws.arn
    :platform: Unix
.. version:: $$VERSION$$
.. moduleauthor:: Patrick Kelley <pkelley@netflix.com>
"""

import re


class ARN(object):
    tech = None
    region = None
    account_number = None
    name = None
    parsed_name = None
    partition = None
    error = False
    root = False
    service = False

    def __init__(self, input):
        arn_match = re.search('^arn:([^:]*):([^:]*):([^:]*):(|\*|[\d]{12}):(.+)$', input)
        if arn_match:
            if arn_match.group(2) == "iam" and arn_match.group(5) == "root":
                self.root = True

            return self._from_arn(arn_match, input)

        acct_number_match = re.search('^(\d{12})+$', input)
        if acct_number_match:
            return self._from_account_number(input)

        aws_service_match = re.search('^([^.]*)\.amazonaws\.com$', input)
        if aws_service_match:
            return self._from_aws_service(input, aws_service_match.group(1))

        self.error = True

    def _from_arn(self, arn_match, input):
        self.partition = arn_match.group(1)
        self.tech = arn_match.group(2)
        self.region = arn_match.group(3)
        self.account_number = arn_match.group(4)
        self.name = arn_match.group(5)

        resource_list = arn_match.group(5).split('/')

        # Handle the longer service level primitives like service roles
        # arn:aws:iam::123456789123:role/aws-service-role/elasticache.amazonaws.com/AWSServiceRoleForElastiCache
        if len(resource_list) == 2:
            self.resource_type = resource_list[0]
            self.resource = resource_list[-1]
        else:
            self.resource_type = resource_list[0]
            self.resource = '/'.join(resource_list[1:])

        self.parsed_name = self.name.split('/')[-1]

    def _from_account_number(self, input):
        self.account_number = input

    def _from_aws_service(self, input, service):
        self.tech = service
        self.service = True

    @staticmethod
    def extract_arns_from_statement_condition(condition):
        condition_subsection \
            = condition.get('ArnEquals', {}) or \
              condition.get('ForAllValues:ArnEquals', {}) or \
              condition.get('ForAnyValue:ArnEquals', {}) or \
              condition.get('ArnLike', {}) or \
              condition.get('ForAllValues:ArnLike', {}) or \
              condition.get('ForAnyValue:ArnLike', {}) or \
              condition.get('StringLike', {}) or \
              condition.get('ForAllValues:StringLike', {}) or \
              condition.get('ForAnyValue:StringLike', {}) or \
              condition.get('StringEquals', {}) or \
              condition.get('ForAllValues:StringEquals', {}) or \
              condition.get('ForAnyValue:StringEquals', {})

        # aws:sourcearn can be found with in lowercase or camelcase or other cases...
        condition_arns = []
        for key, value in condition_subsection.iteritems():
            if key.lower() == 'aws:sourcearn' or key.lower() == 'aws:sourceowner':
                if isinstance(value, list):
                    condition_arns.extend(value)
                else:
                    condition_arns.append(value)

        if not isinstance(condition_arns, list):
            return [condition_arns]
        return condition_arns

