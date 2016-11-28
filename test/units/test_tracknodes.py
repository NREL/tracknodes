import nose
import unittest
from tracknodes.tracknodes import TrackNodes


class TestTrackNodes(unittest.TestCase):

    def test_encode_state(self):
        assert( TrackNodes.encode_state("offline,down") == 3 )

    def test_decode_state(self):
        assert( TrackNodes.decode_state(3) == "offline,down" )

    def test_which(self):
        full_env_path = TrackNodes.which("env")
        assert( full_env_path == "/usr/bin/env" or full_env_path == "/bin/env" )
