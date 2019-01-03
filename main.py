import argparse
import logging
import sys

from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site

from FakeTriblerAPI.endpoints.root_endpoint import RootEndpoint
from FakeTriblerAPI.endpoints.video_root_endpoint import VideoRootEndpoint
from FakeTriblerAPI.tribler_data import TriblerData
import FakeTriblerAPI.tribler_utils as tribler_utils
import FakeTriblerAPI.tribler_data as tribler_data_file


def generate_tribler_data(args):
    tribler_utils.tribler_data = TriblerData()
    tribler_utils.tribler_data.generate()
    tribler_data_file.CREATE_MY_CHANNEL = args.mychannel


def start_api(args):
    logger = logging.getLogger(__file__)

    logger.info("Generating random Tribler data")
    generate_tribler_data(args)

    site = Site(RootEndpoint())
    logger.info("Starting fake Tribler API on port %d", args.port)

    video_site = Site(VideoRootEndpoint())
    logger.info("Starting video API on port %d", tribler_utils.tribler_data.video_player_port)

    reactor.listenTCP(args.port, site)
    reactor.listenTCP(tribler_utils.tribler_data.video_player_port, video_site)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the fake Tribler API.')
    parser.add_argument('-p', '--port', type=int, default=8085, help='the port used to execute code')
    parser.add_argument('--mychannel', type=bool, default=True, help='whether your channel should be created')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.DEBUG)
    log.startLogging(sys.stdout)

    reactor.callWhenRunning(start_api, args)
    reactor.run()
