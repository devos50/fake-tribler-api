import os
from random import randint, sample
from time import time

from FakeTriblerAPI.constants import NEW, TODELETE
from FakeTriblerAPI.models.trustchain_block import TrustchainBlock
from FakeTriblerAPI.models.order import Order
from FakeTriblerAPI.models.tick import Tick
from FakeTriblerAPI.models.transaction import Transaction
from FakeTriblerAPI.utils.network import get_random_port
from models.channel import Channel
from models.download import Download
from models.torrent import Torrent
from models.tunnel import Circuit, Relay, Exit


CREATE_MY_CHANNEL = True


class TriblerData:

    def __init__(self):
        self.channels = []
        self.torrents = []
        self.subscribed_channels = set()
        self.downloads = []
        self.my_channel = -1
        self.settings = {}
        self.trustchain_blocks = []
        self.order_book = {}
        self.transactions = []
        self.orders = []
        self.dht_stats = {}
        self.video_player_port = get_random_port()

    def generate(self):
        self.generate_torrents()
        self.generate_channels()
        self.assign_subscribed_channels()
        self.generate_downloads()
        self.generate_trustchain_blocks()
        self.generate_order_book()
        self.generate_transactions()
        self.generate_orders()
        self.generate_dht_stats()
        self.generate_tunnels()

        # Create settings
        self.settings = {
            "settings": {
                "general": {
                    "family_filter": True,
                    "minport": 1234,
                    "log_dir": "/Users/tribleruser/log",
                },
                "video_server": {
                    "enabled": True,
                    "port": "-1",
                },
                "libtorrent": {
                    "enabled": True,
                    "port": 1234,
                    "proxy_type": 0,
                    "proxy_server": None,
                    "proxy_auth": None,
                    "utp": True,
                    "max_upload_rate": 100,
                    "max_download_rate": 200,
                    "max_connections_download": 5,
                },
                "watch_folder": {
                    "enabled": True,
                    "directory": "/Users/tribleruser/watchfolder",
                },
                "download_defaults": {
                    "seeding_mode": "ratio",
                    "seeding_time": 60,
                    "seeding_ratio": 2.0,
                    "saveas": "bla",
                    "number_hops": 1,
                    "anonymity_enabled": True,
                    "safeseeding_enabled": True,
                },
                "ipv8": {
                    "enabled": True,
                    "use_testnet": False,
                    "statistics": True
                },
                "trustchain": {
                    "enabled": True,
                },
                "tunnel_community": {
                    "exitnode_enabled": True,
                },
                "search_community": {
                    "enabled": True,
                },
                "credit_mining": {
                    "enabled": True,
                    "sources": [],
                    "max_disk_space": 100,
                },
                "resource_monitor": {
                    "enabled": True
                },
                "chant": {
                    "enabled": True,
                    "channel_edit": True
                }
            },
            "ports": {
                "video_server~port": self.video_player_port
            }
        }

    def get_channels(self, first=1, last=50, sort_by=None, sort_asc=True, filter=None, subscribed=False):
        """
        Return channels, based on various parameters.
        """
        filter = filter.lower() if filter else None
        results = self.channels if not subscribed else [self.channels[index] for index in self.subscribed_channels]
        results = [result.get_json() for result in results]

        # Filter on search term
        if filter:
            results = [result for result in results if filter in result['name'].lower()]

        # Sort accordingly
        if sort_by:
            results.sort(key=lambda result: result[sort_by], reverse=not sort_asc)

        return results[first-1:last], len(results)

    def get_torrents(self, first=1, last=50, sort_by=None, sort_asc=True, filter=None, channel_pk=None, include_status=False):
        """
        Return torrents, based on various parameters.
        """
        if channel_pk and not self.get_channel_with_public_key(channel_pk):
            return [], 0

        filter = filter.lower() if filter else None
        results = self.torrents if not channel_pk else self.get_channel_with_public_key(channel_pk).torrents
        results = [result.get_json(include_status=include_status) for result in results]

        # Filter on search term
        if filter:
            results = [result for result in results if filter in result['name'].lower()]

        # Sort accordingly
        if sort_by:
            results.sort(key=lambda result: result[sort_by], reverse=not sort_asc)

        return results[first-1:last], len(results)

    # Generate channels from the random_channels file
    def generate_channels(self):
        num_channels = randint(100, 200)
        for i in range(0, num_channels):
            self.channels.append(Channel(i, name="Channel %d" % i, description="Description of channel %d" % i))

        if CREATE_MY_CHANNEL:
            # Pick one of these channels as your channel
            self.my_channel = randint(0, len(self.channels) - 1)
            channel_obj = self.channels[self.my_channel]
            new_torrents = sample(channel_obj.torrents, min(len(channel_obj.torrents), 10))
            for torrent in new_torrents:
                torrent.status = NEW

            delete_torrents = sample(channel_obj.torrents, min(len(channel_obj.torrents), 10))
            for torrent in delete_torrents:
                torrent.status = TODELETE

    def assign_subscribed_channels(self):
        # Make between 10 and 50 channels subscribed channels
        num_subscribed = randint(10, 20)
        for i in range(0, num_subscribed):
            channel_index = randint(0, len(self.channels) - 1)
            self.subscribed_channels.add(channel_index)
            self.channels[channel_index].subscribed = True

    def generate_torrents(self):
        # Create random torrents in channels
        for _ in xrange(1000):
            self.torrents.append(Torrent.random())

    def get_channel_with_id(self, id):
        for channel in self.channels:
            if str(channel.id) == id:
                return channel

    def get_channel_with_public_key(self, public_key):
        for channel in self.channels:
            if str(channel.public_key) == public_key:
                return channel

    def get_my_channel(self):
        if self.my_channel == -1:
            return None
        return self.channels[self.my_channel]

    def get_download_with_infohash(self, infohash):
        for download in self.downloads:
            if download.torrent.infohash == infohash:
                return download

    def start_random_download(self, media=False):
        random_torrent = sample(self.torrents, 1)[0]
        download = Download(random_torrent)
        if media:
            download.files.append({
                "name": "video.avi",
                "size": randint(1000, 10000000),
                "progress": 1.0,
                "included": True,
                "index": 0
            })
        self.downloads.append(download)

    def generate_downloads(self):
        # Make sure the first download is a media file (so we can play it)
        self.start_random_download(media=True)

        for _ in xrange(randint(10, 30)):
            self.start_random_download()

        # Start some credit mining downloads
        for _ in xrange(randint(1, 5)):
            random_torrent = sample(self.torrents, 1)[0]
            self.downloads.append(Download(random_torrent, is_credit_mining=True))

        # Start some channel downloads
        for _ in xrange(randint(1, 5)):
            random_torrent = sample(self.torrents, 1)[0]
            self.downloads.append(Download(random_torrent, is_channel_download=True))

    def generate_trustchain_blocks(self):
        # Generate a chain of 100 blocks
        my_id = 'a' * 20
        cur_timestamp = time() - 100 * 24 * 3600  # 100 days in the past
        self.trustchain_blocks.append(TrustchainBlock(my_id=my_id, timestamp=cur_timestamp))
        for i in xrange(100):
            cur_timestamp += 24 * 3600
            self.trustchain_blocks.append(TrustchainBlock(my_id=my_id, timestamp=cur_timestamp, last_block=
                                                          self.trustchain_blocks[-1]))

    def generate_order_book(self):
        # Generate some ask/bid ticks
        ask_ticks = [Tick('DUM1', 'DUM2', is_ask=True) for _ in xrange(randint(20, 50))]
        bid_ticks = [Tick('DUM1', 'DUM2', is_ask=False) for _ in xrange(randint(20, 50))]
        self.order_book = {'asks': ask_ticks, 'bids': bid_ticks}

    def get_transaction(self, trader_id, tx_number):
        for transaction in self.transactions:
            if transaction.trader_id == trader_id and transaction.transaction_number == tx_number:
                return transaction

    def generate_transactions(self):
        self.transactions = [Transaction('DUM1', 'DUM2') for _ in xrange(randint(20, 50))]

    def generate_orders(self):
        self.orders = [Order('DUM1', 'DUM2') for _ in xrange(randint(20, 50))]

    def generate_dht_stats(self):
        self.dht_stats = {
            "num_tokens": randint(10, 50),
            "routing_table_buckets": randint(1, 10),
            "num_keys_in_store": randint(100, 500),
            "num_store_for_me": {os.urandom(20).encode('hex'): randint(1, 8)},
            "num_peers_in_store": {},
            "node_id": os.urandom(20).encode('hex'),
            "peer_id": os.urandom(20).encode('hex'),
            "routing_table_size": randint(10, 50)
        }

    def generate_tunnels(self):
        self.tunnel_circuits = [Circuit() for _ in xrange(randint(2, 10))]
        self.tunnel_relays = [Relay() for _ in xrange(randint(2, 10))]
        self.tunnel_exits = [Exit() for _ in xrange(randint(2, 10))]
