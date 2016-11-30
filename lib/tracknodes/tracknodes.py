import sqlite3 as lite
import os
import subprocess
import errno
import re


class TrackNodes:
    def __init__(self, update=False, dbfile=None, nodes_cmd=None, verbose=False):
        """
        Create initial sqlite database and initialize connection
        """
        self.cur = None
        self.con = None
        self.current_failed = []

        self.update = update
        self.dbfile = dbfile
        self.nodes_cmd = TrackNodes.which(nodes_cmd)
        self.verbose = verbose
        self.resourcemanager = None

    def find_nodes_cmd(self):
        """
        Search for nodes command.
        """
        # Look for pbsnodes as option, in PATH, then specific locations
        nodecmd_torque_search_cmds = ["pbsnodes", "/usr/bin/pbsnodes", "/bin/pbsnodes", "/usr/local/bin/pbsnodes"]
        nodecmd_slurm_search_cmds = ["sinfo", "/usr/bin/sinfo", "/bin/sinfo", "/usr/local/bin/sinfo"]
        nodecmd_search_cmds = nodecmd_torque_search_cmds + nodecmd_slurm_search_cmds
        found_node_cmd = True
        if self.nodes_cmd is None:
            found_node_cmd = False
            for node_cmd in nodecmd_search_cmds:
                if TrackNodes.which(node_cmd) is not None:
                    self.nodes_cmd = TrackNodes.which(node_cmd)
                    self.detect_resourcemanager()
                    found_node_cmd = True
                    break
        if found_node_cmd == False:
            raise Exception("Cannot find pbsnodes or sinfo in PATH.")

    def connect_db(self):
        if self.dbfile is None:
            self.dbfile = "%s.%s" % (os.path.realpath(__file__), "db")

        if (False == os.path.isfile(self.dbfile)):
            firstrun = True
        else:
            firstrun = False
        if self.verbose:
            print("tracknodes database: %s" % self.dbfile)

        self.con = lite.connect(self.dbfile)

        with self.con:
            self.cur = self.con.cursor()
            if (True == firstrun):
                self.cur.execute("CREATE TABLE CurrentFailedNodes(Name TEXT, State INT, Comment TEXT)")
                # Use ISO8601 for storing time
                self.cur.execute("CREATE TABLE NodeStates(Name TEXT, State INT, Comment TEXT, Time TEXT)")
                self.con.commit()

    def detect_resourcemanager(self):
        nodes_cmd_base = os.path.basename(self.nodes_cmd).rstrip()
        if nodes_cmd_base == "sinfo":
            self.resourcemanager = "slurm"
        elif nodes_cmd_base == "pbsnodes":
            if self.detect_pbspro() == True:
                self.resourcemanager = "pbspro"
            else:
                self.resourcemanager = "torque"
        else:
            raise Exception("Unable to determine resource manager for nodes_cmd: %s, binary: %s" % (self.nodes_cmd, nodes_cmd_base))

        if self.verbose:
            print("Resource Manager Detected as %s" % self.resourcemanager)

    def online_nodes(self):
        """
        Update database for newly onlined nodes, remove from the online nodes and from the CurrentFailedNodes database
        """
        onlinenodes = []
        found = False

        self.cur.execute("SELECT Name,State,Comment FROM CurrentFailedNodes")
        last_failed = self.cur.fetchall()

        for lx in last_failed:
            found = False
            for cx in self.current_failed:
                if (lx[0] == cx[0]):
                    found = True
                    break
            if (False == found):
                onlinenodes.append(lx)

        for node in onlinenodes:
            self.cur.execute("INSERT INTO NodeStates VALUES(?, ?, ?, datetime('now'))", (node[0], 0, ''))
            self.cur.execute("DELETE FROM CurrentFailedNodes WHERE Name LIKE ?", (node[0],))
            self.con.commit()

    def fail_nodes(self):
        """
        Mark nodes as failed
        """
        for (nodename, state, comment) in self.current_failed:
            self.cur.execute("SELECT Name,State,Comment FROM CurrentFailedNodes WHERE Name LIKE ?", (nodename,))
            node_record = self.cur.fetchone()
            if (None == node_record):
                self.cur.execute("INSERT INTO CurrentFailedNodes VALUES(?, ?, ?)", (nodename, state, comment))
                self.cur.execute("INSERT INTO NodeStates VALUES(?, ?, ?, datetime('now'))", (nodename, state, comment))
                self.con.commit()
            else:
                # Also record historical state and comment changes
                if node_record[0] == nodename and not node_record[2] == comment:
                    self.cur.execute("UPDATE CurrentFailedNodes SET State=?,Comment=? WHERE Name=?", (state, comment, nodename))
                    self.cur.execute("INSERT INTO NodeStates VALUES(?, ?, ?, datetime('now'))", (nodename, state, comment))

    def detect_pbspro(self):
        """
        Detect if its PBSpro vs Torque
        """
        for line in subprocess.Popen([self.nodes_cmd, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].rstrip().split("\n"):
            fields = line.split()
            if fields[0] == "pbs_version":
                return True
            else:
                break
        return False

    def parse_nodes_cmd(self):
        if self.resourcemanager == "torque":
            self.parse_pbsnodes_cmd("-nl")
        elif self.resourcemanager == "pbspro":
            self.parse_pbsnodes_cmd("-l")
        elif self.resourcemanager == "slurm":
            self.parse_sinfo_cmd()
        else:
            raise Exception("Unable to parse nodes_cmd, unsupported resource manager: %s" % self.resourcemanager)

    def parse_pbsnodes_cmd(self, cmd_args):
        """
        Run pbsnodes -nl (Torque) or pbsnodes -l (PBSpro) and parse the output and return an array of tuples [(nodename, state, comment),]
        """
        for line in subprocess.Popen([self.nodes_cmd, cmd_args], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].rstrip().split("\n"):
            fields = line.split()
            if len(fields) == 2:
                self.current_failed.append((fields[0], TrackNodes.encode_state(fields[1]), ''))
            elif len(fields) >= 3:
                self.current_failed.append((fields[0], TrackNodes.encode_state(fields[1]), ' '.join(fields[2::])))
            else:
                if self.verbose:
                    print("Parse Error on line: '%s'" % line)

    def parse_sinfo_cmd(self):
        """
        Run sinfo -dR (slurm) and parse the output and return an array of tuples [(nodename, state, comment),]
        """
        print("test")
        line_num = 0
        for line in subprocess.Popen([self.nodes_cmd, '-dR'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].rstrip().split("\n"):
            # Skip First Line
            if line_num == 0:
                line_num += 1
                continue

            m = re.search(r'^(.*?)\s+([a-zA-Z0-9\-_]+)\s+([0-9\-:T]+)\s+([a-zA-Z0-9_\-]+)$', line)
            if m:
                reason = m.group(1)
                username = m.group(2)
                timestamp = m.group(3)
                nodename = m.group(4)
                # -dR returns only down nodes, so the state is down
                self.current_failed.append((nodename, TrackNodes.encode_state('down'), reason))
            else:
                if self.verbose:
                    print("Parse Error on line: '%s'" % line)

            line_num += 1

    @staticmethod
    def which(program):
        """
        Find Full Path
        """
        def is_exe(fpath):
            """ File must have execute bit set """
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        if program is None:
            return None

        fpath, fname = os.path.split(program)
        if fpath:
            if is_exe(program):
                return program
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, program)
                if is_exe(exe_file):
                    return exe_file

        return None

    @staticmethod
    def encode_state(str):
        """
        Convert from pbsnodes text documentation to binary 0 = online, 1 = offline, 2 = down, 3 = offline|down
        Valid state strings are "free","offline","down","reserve","job-exclusive","job-sharing","busy","time-shared", or "state-unknown".
        """
        state = 0
        if ("free" in str):
            return 0
        if ("offline" in str):
            state = state | 1
        if ("down" in str):
            state = state | 2
        if ("reserve" in str):
            state = state | 4
        if ("job-exclusive" in str):
            state = state | 8
        if ("job-sharing" in str):
            state = state | 16
        if ("busy" in str):
            state = state | 32
        if ("time-shared" in str):
            state = state | 64
        if ("state-unknown" in str):
            state = state | 128
        if (state == 0):
            """ Undetected State """
            state = state | 1024
        return state

    @staticmethod
    def decode_state(state):
        """
        Convert from binary notation to the pbsnodes text documentation
        """
        str = ""
        if (state is None):
            return "undetected-state"
        if (state == 0):
            return "online"
        if (state & 1 == 1):
            str += "offline,"
        if (state & 2 == 2):
            str += "down,"
        if (state & 4 == 4):
            str += "reserve,"
        if (state & 8 == 8):
            str += "job-exclusive,"
        if (state & 16 == 16):
            str += "job-sharing,"
        if (state & 32 == 32):
            str += "busy,"
        if (state & 64 == 64):
            str += "time-shared,"
        if (state & 128 == 128):
            str += "state-unknown,"
        if (state & 1024 == 1024):
            str += "undetected-state,"
        return str.rstrip(",")

    def print_history(self):
        """
        Print database information to STDOUT
        """
        try:
            print("-- History of Node Failures--")
            self.cur.execute("SELECT * FROM NodeStates ORDER BY datetime(Time) DESC")
            rows = self.cur.fetchall()
            for row in rows:
                print("%s | %s | %s | '%s'" % (row[0], row[3], TrackNodes.decode_state(row[1]), row[2]))
            print("-- --")
            print("    ")
        except IOError as e:
            if e.errno == errno.EPIPE:
                # Perhaps output was piped to less and was quit prior to EOF
                return

    def __del__(self):
        """
        Close sqlite connection
        """
        if self.con:
            self.con.close()

    def run(self):
        self.find_nodes_cmd()

        self.connect_db()

        # Get Latest Node Information, Update Database
        if self.update:
            self.parse_nodes_cmd()
            self.online_nodes()
            self.fail_nodes()

        self.print_history()
