from cloudaux.gcp.gce.network import get_network, list_subnetworks
from cloudaux.decorators import modify_output
from flagpole import FlagRegistry, Flags


registry = FlagRegistry()
FLAGS = Flags('BASE')


@registry.register(flag=FLAGS.BASE)
def _get_base(network, **conn):
    result = get_network(Network=network, **conn)
    if 'subnetworks' in result:
        result['subnetworks'] = list_subnetworks(filter='network eq %s' % result['selfLink'], **conn)

    result['_version'] = 1
    return result

@modify_output
def get_network_and_subnetworks(network, flags=FLAGS.ALL, **conn):
    return registry.build_out(flags, network, **conn)
