"""
.. module: cloudaux.tests.aws.test_ec2
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Mike Grima <mgrima@netflix.com>
"""

from cloudaux.orchestration.aws.arn import ARN


def test_arn():

    test_arn = 'arn:aws:iam::123456789123:role/testRole'

    arn = ARN(test_arn)

    assert arn.tech == 'iam'
    assert arn.region == ''
    assert arn.account_number == '123456789123'
    assert arn.name == 'role/testRole'
    assert arn.resource_type == 'role'
    assert arn.resource == 'testRole'

    test_arn2 = 'arn:aws:iam::123456789123:role/service-role/DynamoDBAutoscaleRole'

    arn = ARN(test_arn2)

    assert arn.tech == 'iam'
    assert arn.region == ''
    assert arn.account_number == '123456789123'
    assert arn.name == 'role/service-role/DynamoDBAutoscaleRole'
    assert arn.resource_type == 'role'
    assert arn.resource == 'service-role/DynamoDBAutoscaleRole'
