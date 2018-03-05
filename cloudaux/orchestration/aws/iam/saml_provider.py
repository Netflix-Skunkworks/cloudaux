from cloudaux.aws.iam import get_saml_provider as boto_get_saml_provider
from cloudaux.decorators import modify_output
from flagpole import FlagRegistry, Flags
import defusedxml.ElementTree as ET
from six import string_types


registry = FlagRegistry()
FLAGS = Flags('BASE')


@registry.register(flag=FLAGS.BASE)
def get_base(provider, **conn):
    # Get the SAML Provider information
    saml_provider = boto_get_saml_provider(provider['Arn'], **conn)

    # Parse the SAML Metadata XML Document
    root = ET.fromstring(saml_provider['SAMLMetadataDocument'])

    saml_x509 = ''
    company = ''
    given_name = ''
    email_address = ''

    for parent in root.iter():
        for child in parent:
            if 'X509Certificate' in child.tag:
                saml_x509 = child.text
            if 'Company' in child.tag:
                company = child.text
            if 'GivenName' in child.tag:
                given_name = child.text
            if 'EmailAddress' in child.tag:
                email_address = child.text


    return {
        'Name': root.attrib['entityID'],
        'CreateDate': str(saml_provider['CreateDate']),
        'ValidUntil': str(saml_provider['ValidUntil']),
        'X509': saml_x509,
        'Company': company,
        'GivenName': given_name,
        'Email': email_address
    }


@modify_output
def get_saml_provider(provider, flags=FLAGS.ALL, **conn):

    # If provided an ARN, cast to a dict
    if isinstance(provider, string_types):
        provider = dict(Arn=provider)

    return registry.build_out(flags, start_with=provider, pass_datastructure=True, **conn)
