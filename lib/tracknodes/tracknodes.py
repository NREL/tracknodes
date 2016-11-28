import sqlite3 as lite
import os
import subprocess
import errno


class TrackNodes:
    def __init__(self, update=False, dbfile=None, pbsnodes_cmd=None, verbose=False):
        """
        Create initial sqlite database and initialize connection
        """
        self.cur = None
        self.con = None
        self.current_failed = []

        self.dbfile = dbfile
        self.pbsnodes_cmd = TrackNodes.which(pbsnodes_cmd)
        self.verbose = verbose

        # Look for pbsnodes as option, in PATH, then specific locations
        if self.pbsnodes_cmd is None:
            if TrackNodes.which("pbsnodes") is not None:
                self.pbsnodes_cmd = TrackNodes.which("pbsnodes")
            if TrackNodes.which("/usr/bin/pbsnodes") is not None:
                self.pbsnodes_cmd = "/usr/bin/pbsnodes"
            elif TrackNodes.which("/bin/pbsnodes") is not None:
                self.pbsnodes_cmd = "/bin/pbsnodes"
            elif TrackNodes.which("/usr/local/bin/pbsnodes") is not None:
                self.pbsnodes_cmd = "/usr/local/bin/pbsnodes"
            else:
                raise Exception("Cannot find pbsnodes in PATH.")

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

            # Get Latest Node Information, Update Database
            if update:
                self.parse_pbsnodes()
                self.online_nodes()
                self.fail_nodes()

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

    def parse_pbsnodes(self):
        """
        Run pbsnodes -nl and parse the output and return an array of tuples [(nodename, state, comment),]
        """



        for line in subprocess.Popen([self.pbsnodes_cmd, '-nl'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].rstrip().split("\n"):
            fields = line.split()
            if len(fields) >= 3:
                self.current_failed.append((fields[0], TrackNodes.encode_state(fields[1]), ' '.join(fields[2::])))

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
