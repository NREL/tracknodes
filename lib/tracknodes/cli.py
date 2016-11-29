""" Command Line Interface Module """
import optparse
import os
import yaml
from tracknodes import TrackNodes


class Cli(object):
    """ Command Line Interface for tracknodes """

    def __init__(self):
        """ Setup Arguments and Options for CLI """
        parser = optparse.OptionParser()
        parser.add_option("-U", "--update", dest="update",
                          help="Update Database From PBS",
                          metavar="UPDATE",
                          action="store_true",
                          default=False)
        parser.add_option("-f", "--dbfile", dest="dbfile",
                          help="SQL-Lite Database File",
                          metavar="DBFILE",
                          default=None)
        parser.add_option("-c", "--cmd", dest="cmd",
                          help="binary location, example: /opt/pbsnodes, /opt/sinfo",
                          metavar="CMD",
                          default=None)
        parser.add_option("-v", "--verbose", dest="verbose",
                          help="Verbose Output",
                          metavar="VERBOSE",
                          action="store_true",
                          default=False)
        (options, args) = parser.parse_args()
        self.update = options.update
        self.cmd = options.cmd
        self.dbfile = options.dbfile
        self.verbose = options.verbose

        # Load Configurations if not set on CLI
        if os.path.isfile('/etc/tracknodes.conf'):
            with open('/etc/tracknodes.conf', 'r') as f:
                tracknodes_conf = yaml.load(f)
                if tracknodes_conf is not None:
                    if "dbfile" in tracknodes_conf:
                        if self.dbfile is None:
                            self.dbfile = str(tracknodes_conf["dbfile"])
                    if "cmd" in tracknodes_conf:
                        if self.cmd is None:
                            self.cmd = str(tracknodes_conf["cmd"])

    def run(self):
        """ EntryPoint Of Application """
        tracknodes = TrackNodes(update=self.update, dbfile=self.dbfile, nodes_cmd=self.cmd, verbose=self.verbose)

        tracknodes.run()
