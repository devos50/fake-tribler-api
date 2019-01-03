from random import randint, uniform, choice
import time

from FakeTriblerAPI.constants import COMMITTED
from FakeTriblerAPI.utils import get_random_hex_string, get_random_filename


class Torrent:

    def __init__(self, infohash, name, length, category, status=COMMITTED):
        self.infohash = infohash
        self.name = name
        self.length = length
        self.category = category
        self.files = []
        self.time_added = randint(1200000000, 1460000000)
        self.relevance_score = uniform(0, 20)
        self.status = status

        self.num_seeders = randint(0, 500) if randint(0, 1) == 0 else 0
        self.num_leechers = randint(0, 500) if randint(0, 1) == 0 else 0

    def get_json(self, include_status=False):
        result = {
            "name": self.name,
            "infohash": self.infohash.encode('hex'),
            "size": self.length,
            "category": self.category,
            "relevance_score": self.relevance_score,
            "num_seeders": self.num_seeders,
            "num_leechers": self.num_leechers,
            "last_tracker_check": time.time()
        }

        if include_status:
            result["status"] = self.status

        return result

    @staticmethod
    def random():
        infohash = get_random_hex_string(40).decode('hex')
        name = get_random_filename()
        categories = ['document', 'audio', 'video', 'xxx']
        torrent = Torrent(infohash, name, randint(1024, 1024 * 3000), choice(categories))

        # Create the files
        for _ in xrange(randint(1, 20)):
            torrent.files.append({"path": get_random_filename(), "length": randint(1024, 1024 * 3000)})

        return torrent
