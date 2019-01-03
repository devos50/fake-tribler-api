from twisted.web import resource

from FakeTriblerAPI.endpoints.debug_endpoint import DebugEndpoint
from FakeTriblerAPI.endpoints.downloads_endpoint import DownloadsEndpoint
from FakeTriblerAPI.endpoints.events_endpoint import EventsEndpoint
from FakeTriblerAPI.endpoints.ipv8_endpoint import IPv8Endpoint
from FakeTriblerAPI.endpoints.libtorrent_endpoint import LibTorrentEndpoint
from FakeTriblerAPI.endpoints.market_endpoint import MarketEndpoint
from FakeTriblerAPI.endpoints.metadata_endpoint import MetadataEndpoint
from FakeTriblerAPI.endpoints.mychannel_endpoint import MyChannelEndpoint
from FakeTriblerAPI.endpoints.search_endpoint import SearchEndpoint
from FakeTriblerAPI.endpoints.shutdown_endpoint import ShutdownEndpoint
from FakeTriblerAPI.endpoints.state_endpoint import StateEndpoint
from FakeTriblerAPI.endpoints.statistics_endpoint import StatisticsEndpoint
from FakeTriblerAPI.endpoints.torrentinfo_endpoint import TorrentInfoEndpoint
from FakeTriblerAPI.endpoints.trustchain_endpoint import TrustchainEndpoint
from FakeTriblerAPI.endpoints.settings_endpoint import SettingsEndpoint
from FakeTriblerAPI.endpoints.wallets_endpoint import WalletsEndpoint


class RootEndpoint(resource.Resource):

    def __init__(self):
        resource.Resource.__init__(self)

        self.events_endpoint = EventsEndpoint()
        self.putChild("events", self.events_endpoint)

        child_handler_dict = {"metadata": MetadataEndpoint, "mychannel": MyChannelEndpoint,
                              "settings": SettingsEndpoint, "search": SearchEndpoint,
                              "downloads": DownloadsEndpoint,
                              "trustchain": TrustchainEndpoint, "statistics": StatisticsEndpoint,
                              "state": StateEndpoint, "torrentinfo": TorrentInfoEndpoint,
                              "wallets": WalletsEndpoint, "market": MarketEndpoint, "shutdown": ShutdownEndpoint,
                              "debug": DebugEndpoint, "ipv8": IPv8Endpoint,
                              "libtorrent": LibTorrentEndpoint}

        for path, child_cls in child_handler_dict.iteritems():
            self.putChild(path, child_cls())
