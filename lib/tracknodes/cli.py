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
        parser.add_option("-c", "--pbsnodes_cmd", dest="pbsnodes_cmd",
                          help="pbsnodes binary location, example: /opt/pbsnodes",
                          metavar="PBSNODESCMD",
                          default=None)
        parser.add_option("-v", "--verbose", dest="verbose",
                          help="Verbose Output",
                          metavar="VERBOSE",
                          action="store_true",
                          default=False)
        (options, args) = parser.parse_args()
        self.update = options.update
        self.pbsnodes_cmd = options.pbsnodes_cmd
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
                    if "pbsnodes_cmd" in tracknodes_conf:
                        if self.pbsnodes_cmd is None:
                            self.pbsnodes_cmd = str(tracknodes_conf["pbsnodes_cmd"])

    def run(self):
        """ EntryPoint Of Application """
        pbsnodes = TrackNodes(update=self.update, dbfile=self.dbfile, pbsnodes_cmd=self.pbsnodes_cmd, verbose=self.verbose)
        pbsnodes.print_history()
