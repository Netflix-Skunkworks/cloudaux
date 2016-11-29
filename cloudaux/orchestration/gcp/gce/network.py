from cloudaux.gcp.gce.network import get_network, list_subnetworks
from cloudaux.orchestration import modify

def get_network_and_subnetworks(network, output='camelized', **conn):
    network = get_network(Network=network, **conn)
    if network:
        result = network
        if 'subnetworks' in network:
            subnetworks = list_subnetworks(filter='network eq %s' % network['selfLink'],
                                           **conn)
            result['subnetworks'] = [modify(s, format=output) for s in subnetworks]
        return modify(result, format=output)
    else:
        return None
