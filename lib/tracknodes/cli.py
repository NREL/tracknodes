""" Command Line Interface Module """
from tracknodes import TrackNodes


class Cli(object):
    """ Command Line Interface for tracknodes """

    def __init__(self):
        """ Setup Arguments and Options for CLI """
        pass

    def run(self):
        """ EntryPoint Of Application """
        pbsnodes = TrackNodes()
        pbsnodes.print_history()
