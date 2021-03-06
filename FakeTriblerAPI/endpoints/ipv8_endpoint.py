import json
from twisted.web import resource

from FakeTriblerAPI import tribler_utils


class IPv8Endpoint(resource.Resource):

    def __init__(self):
        resource.Resource.__init__(self)
        self.putChild("trustchain", IPv8TrustChainEndpoint())
        self.putChild("tunnel", IPv8TunnelEndpoint())
        self.putChild("dht", IPv8DHTEndpoint())


class IPv8TrustChainEndpoint(resource.Resource):

    def __init__(self):
        resource.Resource.__init__(self)
        self.putChild("users", IPv8TrustChainUsersEndpoint())


class IPv8TrustChainUsersEndpoint(resource.Resource):

    def getChild(self, path, request):
        return IPv8TrustChainSpecificUserEndpoint(path)


class IPv8TrustChainSpecificUserEndpoint(resource.Resource):

    def __init__(self, _):
        resource.Resource.__init__(self)
        self.putChild("blocks", IPv8TrustChainSpecificUserBlocksEndpoint())


class IPv8TrustChainSpecificUserBlocksEndpoint(resource.Resource):

    def render_GET(self, request):
        return json.dumps({"blocks": [block.to_dictionary() for block in tribler_utils.tribler_data.trustchain_blocks]})


class IPv8TunnelEndpoint(resource.Resource):

    def __init__(self):
        resource.Resource.__init__(self)
        self.putChild("circuits", IPv8CircuitsEndpoint())
        self.putChild("relays", IPv8RelaysEndpoint())
        self.putChild("exits", IPv8ExitsEndpoint())


class IPv8CircuitsEndpoint(resource.Resource):

    def render_GET(self, request):
        return json.dumps({"circuits": [circuit.to_dictionary() for circuit in tribler_utils.tribler_data.tunnel_circuits]})


class IPv8RelaysEndpoint(resource.Resource):

    def render_GET(self, request):
        return json.dumps({"relays": [relay.to_dictionary() for relay in tribler_utils.tribler_data.tunnel_relays]})


class IPv8ExitsEndpoint(resource.Resource):

    def render_GET(self, request):
        return json.dumps({"exits": [exit_socket.to_dictionary() for exit_socket in tribler_utils.tribler_data.tunnel_exits]})


class IPv8DHTEndpoint(resource.Resource):

    def __init__(self):
        resource.Resource.__init__(self)
        self.putChild("statistics", IPv8DHTStatisticsEndpoint())


class IPv8DHTStatisticsEndpoint(resource.Resource):

    def render_GET(self, request):
        return json.dumps({"statistics": tribler_utils.tribler_data.dht_stats})
