import os
import unittest
from unittest import mock
from auto_di_tag import rename, tag, create_playlist_files


class TestAutoDiTag(unittest.TestCase):

    @mock.patch("builtins.open", new_callable=mock.mock_open,
                read_data="01_Waltz; Artist -- Dance\n02_Tango; Artist -- Dance\n")
    @mock.patch("os.rename")
    @mock.patch("os.listdir", return_value=["01-Song.mp3", "02-Song.mp3"])
    @mock.patch("os.path.exists")
    @mock.patch("os.path.isfile")
    @mock.patch("os.path.isdir")
    def test_rename(self, mock_isdir, mock_isfile, mock_exists, mock_listdir, mock_rename, mock_open):
        # Mock file and directory existence
        def exists_side_effect(path):
            return path in ["/fake/dir", "fakefile.txt"]

        mock_exists.side_effect = exists_side_effect
        mock_isfile.side_effect = lambda path: path == "fakefile.txt"
        mock_isdir.side_effect = lambda path: path == "/fake/dir"

        args = mock.Mock()
        args.dir = "/fake/dir"
        args.file = "fakefile.txt"

        rename(args)

        self.assertEqual(mock_rename.call_count, 2)
        mock_rename.assert_any_call("/fake/dir/01-Song.mp3", "/fake/dir/01_Waltz; Artist -- Dance.mp3")
        mock_rename.assert_any_call("/fake/dir/02-Song.mp3", "/fake/dir/02_Tango; Artist -- Dance.mp3")

    @mock.patch("os.listdir", return_value=[
        "01_Title; Artist -- Style.mp3",
    ])
    @mock.patch("auto_di_tag.apply_tags")
    @mock.patch("os.path.exists", return_value=True)
    @mock.patch("os.path.isdir", return_value=True)
    def test_tag(self, mock_isdir, mock_exists, mock_apply_tags, mock_listdir):
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
    @mock.patch("os.path.exists", return_value=True)
    @mock.patch("os.path.isdir", return_value=True)
    def test_create_playlist_files(self, mock_isdir, mock_exists, mock_open, mock_mp3, mock_listdir, mock_copy):
        mock_audio = mock.Mock()
        mock_audio.info.length = 123.45
        mock_mp3.return_value = mock_audio  # <-- MP3 is fully mocked

        args = mock.Mock()
        args.name = "MyPlaylist"
        args.dir = "music"

        create_playlist_files(args)

        mock_open.assert_called_once_with("./MyPlaylist.m3u", "w", encoding='utf-8')
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


# New test class for validation functions
class TestValidationFunctions(unittest.TestCase):

    @mock.patch("os.path.exists", return_value=False)
    def test_validate_descriptor_file_not_found(self, mock_exists):
        from auto_di_tag import validate_descriptor_file, DescriptorFileError

        with self.assertRaises(DescriptorFileError) as cm:
            validate_descriptor_file("nonexistent.txt")

        self.assertIn("Descriptor file not found", str(cm.exception))

    @mock.patch("builtins.open", new_callable=mock.mock_open,
                read_data="01_Song; Artist -- Dance\n02_Bad,Format; Artist -- Dance\n")
    @mock.patch("os.path.exists", return_value=True)
    @mock.patch("os.path.isfile", return_value=True)
    def test_validate_descriptor_file_comma_allowed(self, mock_isfile, mock_exists, mock_open):
        """Test that commas in song titles are allowed"""
        from auto_di_tag import validate_descriptor_file

        # This should NOT raise an error - commas in titles are allowed
        result = validate_descriptor_file("test.txt")
        self.assertEqual(len(result), 2)
        self.assertIn("Bad,Format", result[1])

    @mock.patch("builtins.open", new_callable=mock.mock_open, read_data="01_Song, Artist -- Dance\n")
    @mock.patch("os.path.exists", return_value=True)
    @mock.patch("os.path.isfile", return_value=True)
    def test_validate_descriptor_file_comma_instead_of_semicolon(self, mock_isfile, mock_exists, mock_open):
        from auto_di_tag import validate_descriptor_file, DescriptorFileError

        with self.assertRaises(DescriptorFileError) as cm:
            validate_descriptor_file("test.txt")

        error_msg = str(cm.exception)
        self.assertIn("Line 1", error_msg)
        self.assertIn("Found comma (,) but expected semicolon (;)", error_msg)

    @mock.patch("builtins.open", new_callable=mock.mock_open, read_data="01_Song; Artist - Dance\n")
    @mock.patch("os.path.exists", return_value=True)
    @mock.patch("os.path.isfile", return_value=True)
    def test_validate_descriptor_file_single_dash_error(self, mock_isfile, mock_exists, mock_open):
        from auto_di_tag import validate_descriptor_file, DescriptorFileError

        with self.assertRaises(DescriptorFileError) as cm:
            validate_descriptor_file("test.txt")

        error_msg = str(cm.exception)
        self.assertIn("Line 1", error_msg)
        self.assertIn("Found single dash (-) but expected double dash (--)", error_msg)

    @mock.patch("builtins.open", new_callable=mock.mock_open, read_data="03_Song; Artist -- Dance\n")
    @mock.patch("os.path.exists", return_value=True)
    @mock.patch("os.path.isfile", return_value=True)
    def test_validate_descriptor_file_track_number_mismatch(self, mock_isfile, mock_exists, mock_open):
        from auto_di_tag import validate_descriptor_file, DescriptorFileError

        with self.assertRaises(DescriptorFileError) as cm:
            validate_descriptor_file("test.txt")

        error_msg = str(cm.exception)
        self.assertIn("Line 1", error_msg)
        self.assertIn("Track number mismatch", error_msg)
        self.assertIn("Expected '01'", error_msg)
        self.assertIn("but found '03'", error_msg)

    @mock.patch("builtins.open", new_callable=mock.mock_open,
                read_data="01_Song; Artist -- Dance\n02_Another Song, With Comma; Artist -- Style\n")
    @mock.patch("os.path.exists", return_value=True)
    @mock.patch("os.path.isfile", return_value=True)
    def test_validate_descriptor_file_valid(self, mock_isfile, mock_exists, mock_open):
        from auto_di_tag import validate_descriptor_file

        result = validate_descriptor_file("test.txt")

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "01_Song; Artist -- Dance")
        self.assertEqual(result[1], "02_Another Song, With Comma; Artist -- Style")

    @mock.patch("os.path.exists", return_value=False)
    def test_validate_music_directory_not_found(self, mock_exists):
        from auto_di_tag import validate_music_directory, AudioFileError

        with self.assertRaises(AudioFileError) as cm:
            validate_music_directory("nonexistent")

        self.assertIn("Music directory not found", str(cm.exception))

    @mock.patch("os.listdir", return_value=[])
    @mock.patch("os.path.exists", return_value=True)
    @mock.patch("os.path.isdir", return_value=True)
    def test_validate_music_directory_empty(self, mock_isdir, mock_exists, mock_listdir):
        from auto_di_tag import validate_music_directory, AudioFileError

        with self.assertRaises(AudioFileError) as cm:
            validate_music_directory("empty_dir")

        self.assertIn("Music directory is empty", str(cm.exception))


class TestParseFilename(unittest.TestCase):

    def test_parse_filename_valid(self):
        from auto_di_tag import parse_filename

        result = parse_filename("01_Title; Artist -- Dance.mp3")
        self.assertEqual(result, ("01", "Title", "Artist", "Dance"))

    def test_parse_filename_invalid(self):
        from auto_di_tag import parse_filename

        result = parse_filename("invalid_format.mp3")
        self.assertIsNone(result)

    def test_parse_filename_no_mp3_extension(self):
        from auto_di_tag import parse_filename

        result = parse_filename("01_Title; Artist -- Dance.txt")
        self.assertIsNone(result)