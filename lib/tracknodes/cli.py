""" Command Line Interface Module """

from tracknodes import TrackNodes


class Cli(object):
    """ Command Line Interface for tracknodes """

    def __init__(self):
        """ Setup Arguments and Options for CLI """
        self.tracknodes = TrackNodes()

    def run(self):
        """ EntryPoint Of Application """
        self.tracknodes.parse_args()
        self.tracknodes.parse_configfile()
        self.tracknodes.run()
