import nose
import mock
import unittest
import sys
import types
from StringIO import StringIO
from tracknodes.tracknodes import TrackNodes


class mock_Popen(object):
    pass


def mock_communicate_sinfo(self):
    return ["\nbroken ram root 2017-01-02T09:09:82 n010\n",]


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

    @mock.patch('tracknodes.tracknodes.TrackNodes.which', return_value="pbsnodes")
    def test_run(self, mock_which):
        out = StringIO()
        orig_stdout = sys.stdout
        sys.stdout = out

        tn = TrackNodes(nodes_cmd="pbsnodes")

        tn.run()

        sys.stdout = orig_stdout

        print(out.getvalue())

        assert( "History of Node Failures" in out.getvalue() )

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

        assert( "n010 | 2016-11-30 20:27:04 | down | 'broken ram'" in out.getvalue() )
