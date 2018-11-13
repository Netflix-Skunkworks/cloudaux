"""
.. module: cloudaux.orchestration.aws.iam.server_certificate
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Mike Grima <mgrima@netflix.com>
"""
from cloudaux import get_iso_string
from cloudaux.aws.iam import get_server_certificate as get_server_certificate_api
from cloudaux.decorators import modify_output
from flagpole import FlagRegistry, Flags

from cloudaux.orchestration import modify
from cloudaux.orchestration.aws import _conn_from_args
from cloudaux.orchestration.aws.iam import MissingFieldException

registry = FlagRegistry()
FLAGS = Flags('BASE')


@registry.register(flag=FLAGS.BASE)
def _get_base(server_certificate, **conn):
    """Fetch the base IAM Server Certificate."""
    server_certificate['_version'] = 1

    # Get the initial cert details:
    cert_details = get_server_certificate_api(server_certificate['ServerCertificateName'], **conn)

    if cert_details:
        server_certificate.update(cert_details['ServerCertificateMetadata'])
        server_certificate['CertificateBody'] = cert_details['CertificateBody']
        server_certificate['CertificateChain'] = cert_details.get('CertificateChain', None)

        # Cast dates from a datetime to something JSON serializable.
        server_certificate['UploadDate'] = get_iso_string(server_certificate['UploadDate'])
        server_certificate['Expiration'] = get_iso_string(server_certificate['Expiration'])

    return server_certificate


@modify_output
def get_server_certificate(server_certificate, flags=FLAGS.BASE, **conn):
    """
    Orchestrates all the calls required to fully build out an IAM User in the following format:

    {
        "Arn": ...,
        "ServerCertificateName": ...,
        "Path": ...,
        "ServerCertificateId": ...,
        "UploadDate": ...,  # str
        "Expiration": ...,  # str
        "CertificateBody": ...,
        "CertificateChain": ...,
        "_version": 1
    }

    :param flags: By default, Users is disabled. This is somewhat expensive as it has to call the
                  `get_server_certificate` call multiple times.
    :param server_certificate: dict MUST contain the ServerCertificateName and also a combination of
                               either the ARN or the account_number.
    :param output: Determines whether keys should be returned camelized or underscored.
    :param conn: dict containing enough information to make a connection to the desired account.
                 Must at least have 'assume_role' key.
    :return: dict containing fully built out Server Certificate.
    """
    if not server_certificate.get('ServerCertificateName'):
        raise MissingFieldException('Must include ServerCertificateName.')

    server_certificate = modify(server_certificate, output='camelized')
    _conn_from_args(server_certificate, conn)
    return registry.build_out(flags, start_with=server_certificate, pass_datastructure=True, **conn)
