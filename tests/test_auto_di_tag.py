import os
import unittest
from unittest import mock
from auto_di_tag import rename, tag, create_playlist_files


class TestAutoDiTag(unittest.TestCase):

    @mock.patch("builtins.open", new_callable=mock.mock_open, read_data="Waltz\nTango\n")
    @mock.patch("os.rename")
    @mock.patch("os.listdir", return_value=["01-Song.mp3", "02-Song.mp3"])
    def test_rename(self, mock_listdir, mock_rename, mock_open):
        args = mock.Mock()
        args.dir = "/fake/dir"
        args.file = "fakefile.txt"

        rename(args)

        self.assertEqual(mock_rename.call_count, 2)
        mock_rename.assert_any_call("/fake/dir/01-Song.mp3", "/fake/dir/Waltz.mp3")
        mock_rename.assert_any_call("/fake/dir/02-Song.mp3", "/fake/dir/Tango.mp3")

    @mock.patch("os.listdir", return_value=[
        "01_Title; Artist -- Style.mp3",
    ])
    @mock.patch("auto_di_tag.apply_tags")
    def test_tag(self, mock_apply_tags, mock_listdir):
        args = mock.Mock()
        args.dir = "/fake/music"
        args.name = "Dance Album"

        tag(args)

        mock_apply_tags.assert_called_once_with(
            os.path.join("/fake/music", "01_Title; Artist -- Style.mp3"),
            "01", "Title", "Artist", "Style", "Dance Album"
        )

    @mock.patch("shutil.copy")
    @mock.patch("os.listdir", return_value=["01_Title; Artist -- Style.mp3"])
    @mock.patch("auto_di_tag.MP3")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    def test_create_playlist_files(self, mock_open, mock_mp3, mock_listdir, mock_copy):
        mock_audio = mock.Mock()
        mock_audio.info.length = 123.45
        mock_mp3.return_value = mock_audio  # <-- MP3 is fully mocked

        args = mock.Mock()
        args.name = "MyPlaylist"
        args.dir = "music"

        create_playlist_files(args)

        mock_open.assert_called_once_with("./MyPlaylist.m3u", "w")
        handle = mock_open()
        written = ''.join(handle.writelines.call_args[0][0])

        assert "#EXTM3U" in written
        assert "#EXTINF:123,Artist - Title" in written
        assert "music/01_Title%3B%20Artist%20--%20Style.mp3" in written

        mock_copy.assert_called_once_with("./MyPlaylist.m3u", "./MyPlaylist.m3u8")


import sys
from auto_di_tag import get_args


class TestGetArgs(unittest.TestCase):

    @mock.patch("sys.argv", [
        "auto_di_tag.py",
        "-f", "playlist.txt",
        "-d", "music_dir",
        "-n", "My Playlist"
    ])
    def test_get_args_valid(self):
        args = get_args()
        self.assertEqual(args.file, "playlist.txt")
        self.assertEqual(args.dir, "music_dir")
        self.assertEqual(args.name, "My Playlist")

    @mock.patch("sys.argv", ["auto_di_tag.py"])
    def test_get_args_missing_required(self):
        with self.assertRaises(SystemExit) as cm:
            get_args()
        self.assertEqual(cm.exception.code, 2)  # argparse uses exit code 2 for bad usage

import os
import shutil
import tempfile
import unittest
from auto_di_tag import rename


class TestRenameIntegration(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "tänze.txt")

        # Copy the real examples/tänze.txt to temp location
        shutil.copy("examples/tänze.txt", self.test_file)

        # Create fake mp3 files to rename
        for i in range(1, 52):
            name = f"{i:02d}-song.mp3"
            with open(os.path.join(self.test_dir, name), "w") as f:
                f.write("dummy audio content")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_rename_creates_correct_names(self):
        args = type("Args", (), {})()
        args.dir = self.test_dir
        args.file = self.test_file

        rename(args)

        # Verify renamed files match names in tänze.txt
        with open(self.test_file, "r", encoding="utf-8") as f:
            expected_names = [line.strip() + ".mp3" for line in f if line.strip()]

        current_files = os.listdir(self.test_dir)
        for expected in expected_names:
            self.assertIn(expected, current_files)
