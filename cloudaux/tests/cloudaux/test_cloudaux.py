"""
.. module: cloudaux.tests.cloudaux.test_cloudaux
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Patrick Kelley <patrickk@23andme.com>
"""
from cloudaux import CloudAux


def test_cloudaux():
    conn_one = {
        "account_number": "111111111111",
        "assume_role": "role_one",
        "region": "us-east-1",
        "session_name": "conn_one"
    }

    conn_two = {
        "account_number": "222222222222",
        "assume_role": "role_two",
        "region": "us-east-2",
        "session_name": "conn_two"
    }

    ca_one = CloudAux(**conn_one)
    ca_two = CloudAux(**conn_two)

    assert ca_one.conn_details["account_number"] == "111111111111"
    assert ca_one.conn_details["assume_role"] == "role_one"
    assert ca_one.conn_details["region"] == "us-east-1"
    assert ca_one.conn_details["session_name"] == "conn_one"

    assert ca_two.conn_details["account_number"] == "222222222222"
    assert ca_two.conn_details["assume_role"] == "role_two"
    assert ca_two.conn_details["region"] == "us-east-2"
    assert ca_two.conn_details["session_name"] == "conn_two"
