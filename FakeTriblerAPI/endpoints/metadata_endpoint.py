import json
from random import sample

from twisted.web import http, resource

import FakeTriblerAPI.tribler_utils as tribler_utils


class MetadataEndpoint(resource.Resource):

    def __init__(self):
        resource.Resource.__init__(self)

        child_handler_dict = {
            "channels": ChannelsEndpoint,
            "torrents": TorrentsEndpoint
        }

        for path, child_cls in child_handler_dict.iteritems():
            self.putChild(path, child_cls())


class BaseChannelsEndpoint(resource.Resource):

    @staticmethod
    def return_404(request, message="the channel with the provided cid is not known"):
        """
        Returns a 404 response code if your channel has not been created.
        """
        request.setResponseCode(http.NOT_FOUND)
        return json.dumps({"error": message})


class ChannelsEndpoint(BaseChannelsEndpoint):

    def __init__(self):
        BaseChannelsEndpoint.__init__(self)

        child_handler_dict = {
            "popular": ChannelsPopularEndpoint
        }
        for path, child_cls in child_handler_dict.iteritems():
            self.putChild(path, child_cls())

    def getChild(self, path, request):
        if path == "popular":
            return ChannelsPopularEndpoint()

        return SpecificChannelEndpoint(path)

    @staticmethod
    def sanitize_parameters(parameters):
        """
        Sanitize the parameters and check whether they exist
        """
        first = 1 if 'first' not in parameters else int(parameters['first'][0])  # TODO check integer!
        last = 50 if 'last' not in parameters else int(parameters['last'][0])  # TODO check integer!
        sort_by = None if 'sort_by' not in parameters else parameters['sort_by'][0]  # TODO check integer!
        sort_asc = True if 'sort_asc' not in parameters else bool(int(parameters['sort_asc'][0]))
        filter = None if 'filter' not in parameters else parameters['filter'][0]

        subscribed = False
        if 'subscribed' in parameters:
            subscribed = bool(int(parameters['subscribed'][0]))

        return first, last, sort_by, sort_asc, filter, subscribed

    def render_GET(self, request):
        first, last, sort_by, sort_asc, filter, subscribed = ChannelsEndpoint.sanitize_parameters(request.args)
        channels, total = tribler_utils.tribler_data.get_channels(first, last, sort_by, sort_asc, filter, subscribed)
        return json.dumps({
            "channels": channels,
            "first": first,
            "last": last,
            "sort_by": sort_by,
            "sort_asc": int(sort_asc),
            "total": total
        })


class SpecificChannelEndpoint(resource.Resource):

    def __init__(self, channel_pk):
        resource.Resource.__init__(self)
        self.channel_pk = channel_pk.decode('hex')

        self.putChild("torrents", SpecificChannelTorrentsEndpoint(self.channel_pk))

    def render_POST(self, request):
        parameters = http.parse_qs(request.content.read(), 1)
        if 'subscribe' not in parameters:
            request.setResponseCode(http.BAD_REQUEST)
            return json.dumps({"success": False, "error": "subscribe parameter missing"})

        to_subscribe = bool(int(parameters['subscribe'][0]))
        channel = tribler_utils.tribler_data.get_channel_with_public_key(self.channel_pk)
        if channel is None:
            return BaseChannelsEndpoint.return_404(request)

        if to_subscribe:
            tribler_utils.tribler_data.subscribed_channels.add(channel.id)
            channel.subscribed = True
        else:
            if channel.id in tribler_utils.tribler_data.subscribed_channels:
                tribler_utils.tribler_data.subscribed_channels.remove(channel.id)
            channel.subscribed = False

        return json.dumps({"success": True})


class SpecificChannelTorrentsEndpoint(BaseChannelsEndpoint):

    def __init__(self, channel_pk):
        BaseChannelsEndpoint.__init__(self)
        self.channel_pk = channel_pk

    @staticmethod
    def sanitize_parameters(parameters):
        """
        Sanitize the parameters and check whether they exist
        """
        first = 1 if 'first' not in parameters else int(parameters['first'][0])  # TODO check integer!
        last = 50 if 'last' not in parameters else int(parameters['last'][0])  # TODO check integer!
        sort_by = None if 'sort_by' not in parameters else parameters['sort_by'][0]  # TODO check integer!
        sort_asc = True if 'sort_asc' not in parameters else bool(int(parameters['sort_asc'][0]))
        filter = None if 'filter' not in parameters else parameters['filter'][0]

        channel = ''
        if 'channel' in parameters:
            channel = parameters['channel'][0].decode('hex')

        return first, last, sort_by, sort_asc, filter, channel

    def render_GET(self, request):
        first, last, sort_by, sort_asc, filter, channel = SpecificChannelTorrentsEndpoint.sanitize_parameters(
            request.args)
        channel_obj = tribler_utils.tribler_data.get_channel_with_public_key(self.channel_pk)
        if not channel_obj:
            return SpecificChannelTorrentsEndpoint.return_404(request)

        torrents, total = tribler_utils.tribler_data.get_torrents(first, last, sort_by, sort_asc, filter, channel)
        return json.dumps({
            "torrents": torrents,
            "first": first,
            "last": last,
            "sort_by": sort_by,
            "sort_asc": int(sort_asc),
            "total": total
        })


class ChannelsPopularEndpoint(BaseChannelsEndpoint):

    def render_GET(self, request):
        results_json = [channel.get_json() for channel in sample(tribler_utils.tribler_data.channels, 20)]
        return json.dumps({"channels": results_json})


class TorrentsEndpoint(resource.Resource):

    def __init__(self):
        resource.Resource.__init__(self)
        self.putChild("random", TorrentsRandomEndpoint())


class TorrentsRandomEndpoint(resource.Resource):

    def render_GET(self, request):
        return json.dumps({"torrents": [torrent.get_json() for torrent in sample(tribler_utils.tribler_data.torrents, 20)]})
