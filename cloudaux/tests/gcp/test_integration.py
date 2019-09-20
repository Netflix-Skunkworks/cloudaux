import pytest
import os

from cloudaux.gcp.gcs import (
    list_buckets,
    list_objects_in_bucket,
)
from cloudaux.gcp.iam import get_project_iam_policy
from cloudaux.gcp.gce.project import get_project
from cloudaux.gcp.crm import get_iam_policy
from cloudaux.gcp.gce.address import (
    list_addresses,
    list_global_addresses,
)
from cloudaux.gcp.gce.disk import (
    list_disks,
)
from cloudaux.gcp.gce.forwarding_rule import (
    list_forwarding_rules,
    list_global_forwarding_rules,
)
from cloudaux.gcp.gce.instance import (
    list_instances
)
from cloudaux.gcp.gce.zone import (
    list_zones
)

@pytest.fixture
def project():
    return os.getenv('CLOUDAUX_GCP_TEST_PROJECT')

@pytest.mark.skipif(
    os.getenv('CLOUDAUX_GCP_TEST_PROJECT') is None,
    reason="Cannot run integration tests unless GCP project configured"
)
@pytest.mark.parametrize('function,p_param', [
    (list_addresses, 'project'),
    (list_forwarding_rules, 'project'),
    (list_global_addresses, 'project'),
    (list_global_forwarding_rules, 'project'),
    (get_iam_policy, 'resource'),
    (get_project, 'project'),
    (get_project_iam_policy, 'resource'),
])
def test_cloudaux_gcp_global_integration(function, p_param, project):
    result = function(**{p_param: project})
    assert result is not None

@pytest.mark.skipif(
    os.getenv('CLOUDAUX_GCP_TEST_PROJECT') is None,
    reason="Cannot run integration tests unless GCP project configured"
)
@pytest.mark.parametrize('function,p_param,z_param', [
    (list_disks, 'project', 'zone'),
    (list_instances, 'project', 'zone'),
])
def test_cloudaux_gcp_zoned_integration(function, p_param, z_param, project):
    for zone in list_zones(project=project):
        result = function(**{p_param: project, z_param: zone['name']})
        assert result is not None

@pytest.mark.skipif(
    os.getenv('CLOUDAUX_GCP_TEST_PROJECT') is None,
    reason="Cannot run integration tests unless GCP project configured"
)
def test_cloudaux_gcs(project):
    for bucket in list_buckets(project=project):
        for bucket_object in list_objects_in_bucket(Bucket=bucket['name']):
            assert bucket_object is not None
