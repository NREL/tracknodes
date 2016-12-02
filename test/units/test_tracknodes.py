import nose
import mock
import unittest
import sys
import types
from tracknodes.tracknodes import TrackNodes

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class mock_Popen(object):
    pass

class ContextualStringIO(StringIO):
    def __enter__(self):
        return self
    def __exit__(self, *args):
        self.close() # icecrime does it, so I guess I should, too
        return False # Indicate that we haven't handled the exception, if received

def mock_communicate_sinfo(self):
    return ["\nbroken ram root 2017-01-02T09:09:82 n010\n",]

def mock_communicate_torque_version(self):
    return ["", "Version: 12"]

def mock_communicate_pbspro_version(self):
    return ["", "pbs_version = 14.1.0"]


class TestTrackNodes(unittest.TestCase):

    def test_encode_state(self):
        assert( TrackNodes.encode_state("offline,down") == 3 )

    def test_decode_state(self):
        assert( TrackNodes.decode_state(3) == "offline,down" )

    def test_which_shortpath(self):
        full_env_path = TrackNodes.which("env")
        assert( full_env_path == "/usr/bin/env" or full_env_path == "/bin/env" )

    def test_detect_resourcemanager_slurm_fullpath(self):
        tn = TrackNodes()
        tn.nodes_cmd = "/usr/bin/sinfo"
        tn.detect_resourcemanager()
        assert( tn.resourcemanager == "slurm" )

    def test_detect_resourcemanager_slurm_shortpath(self):
        tn = TrackNodes()
        tn.nodes_cmd = "sinfo"
        tn.detect_resourcemanager()
        assert( tn.resourcemanager == "slurm" )

    @mock.patch('tracknodes.tracknodes.TrackNodes.which', return_value="sinfo")
    def test_run(self, mock_which):
        out = StringIO()
        orig_stdout = sys.stdout
        sys.stdout = out

        tn = TrackNodes(nodes_cmd="sinfo")
        tn.resourcemanager="slurm"
        tn.run()

        sys.stdout = orig_stdout

        print(out.getvalue())

        assert( "History of Nodes" in out.getvalue() )

    @mock.patch('tracknodes.tracknodes.TrackNodes.which', return_value="sinfo")
    def test_run_verbose(self, mock_which):
        out = StringIO()
        orig_stdout = sys.stdout
        sys.stdout = out

        tn = TrackNodes(nodes_cmd="sinfo", verbose=True)
        tn.resourcemanager="slurm"
        tn.run()

        sys.stdout = orig_stdout

        print(out.getvalue())

        assert( "Resource Manager Detected" in out.getvalue() )

    @mock.patch('tracknodes.tracknodes.Popen')
    @mock.patch('tracknodes.tracknodes.TrackNodes.which', return_value="sinfo")
    def test_run_update(self, mock_which, mock_popen):
        mock_popen.return_value = mock_Popen()
        mock_popen.return_value.communicate = types.MethodType(mock_communicate_sinfo, mock_popen.return_value)

        out = StringIO()
        orig_stdout = sys.stdout
        sys.stdout = out

        tn = TrackNodes(update=True, nodes_cmd="sinfo")
        tn.resourcemanager="slurm"
        tn.run()

        sys.stdout = orig_stdout

        print(out.getvalue())

        assert( "| down | 'broken ram'" in out.getvalue() )

    @mock.patch('tracknodes.tracknodes.TrackNodes.which', return_value="sinfo")
    def test_find_nodes_cmd(self, mock_which):
        tn = TrackNodes()
        tn.find_nodes_cmd()

        print( tn.nodes_cmd )
        assert( tn.nodes_cmd == "sinfo" )

    @mock.patch('tracknodes.tracknodes.Popen')
    @mock.patch('tracknodes.tracknodes.TrackNodes.which', return_value="pbsnodes")
    def test_detect_resourcemanager_pbspro(self, mock_which, mock_popen):
        mock_popen.return_value = mock_Popen()
        mock_popen.return_value.communicate = types.MethodType(mock_communicate_pbspro_version, mock_popen.return_value)

        tn = TrackNodes(nodes_cmd="pbsnodes")
        tn.detect_resourcemanager()

        print( tn.resourcemanager )

        assert( tn.resourcemanager == "pbspro" )

    @mock.patch('tracknodes.tracknodes.Popen')
    @mock.patch('tracknodes.tracknodes.TrackNodes.which', return_value="pbsnodes")
    def test_detect_resourcemanager_torque(self, mock_which, mock_popen):
        mock_popen.return_value = mock_Popen()
        mock_popen.return_value.communicate = types.MethodType(mock_communicate_torque_version, mock_popen.return_value)

        tn = TrackNodes(nodes_cmd="pbsnodes")
        tn.detect_resourcemanager()

        print( tn.resourcemanager )

        assert( tn.resourcemanager == "torque" )

    @mock.patch('tracknodes.tracknodes.os.path.isfile', return_value=True)
    @mock.patch('tracknodes.tracknodes.open', create=True)
    def test_parse_configfile(self, mock_open, mock_isfile):
        mock_open.return_value = ContextualStringIO("---\ncmd: 'sinfo'\ndbfile: '/tmp/test.db'\n")

        tn = TrackNodes()
        tn.parse_configfile()

        assert ( tn.nodes_cmd == 'sinfo' and tn.dbfile == '/tmp/test.db' )
