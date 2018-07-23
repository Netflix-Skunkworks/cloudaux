"""
.. module: cloudaux.tests.aws.test_iam
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Will Bengtson <wbengtson@netflix.com>
"""

from cloudaux.aws.iam import get_account_authorization_details


def test_get_account_authorization_details_role(test_role):
    # TODO: Finish out tests once moto PR is merged
    # result = get_account_authorization_details('Role')

    assert 1 == 1
