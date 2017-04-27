from cloudaux.gcp.gce.network import get_network, list_subnetworks
from cloudaux.orchestration import modify
from cloudaux.orchestration.flag_registry import FlagRegistry, Flags


class GCENetworkFlagRegistry(FlagRegistry):
    from collections import defaultdict
    r = defaultdict(list)


FLAGS = Flags('BASE')


@GCENetworkFlagRegistry.register(flag=FLAGS.BASE)
def _get_base(network, **conn):
    result = get_network(Network=network, **conn)
    if 'subnetworks' in result:
        subnetworks = list_subnetworks(filter='network eq %s' % result['selfLink'], **conn)
        result['subnetworks'] = [modify(s, format=output) for s in subnetworks]

    result['_version'] = 1
    return result


def get_network_and_subnetworks(network, output='camelized', flags=FLAGS.ALL, **conn):
    result = dict()
    GCENetworkFlagRegsitry.build_out(result, flags, network, **conn)
    return modify(result, format=output)
