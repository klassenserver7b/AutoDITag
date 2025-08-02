import argparse
import re
import os
import shutil
import urllib.parse
import sys
from typing import Optional, Tuple, List
from mutagen.id3 import ID3, TIT2, TALB, TRCK, TRK, TPE1, TPE2, TCON, TCOM, COMM
from mutagen.mp3 import MP3


class AutoDITagError(Exception):
    """Base exception for AutoDITag errors"""
    pass


class DescriptorFileError(AutoDITagError):
    """Exception for descriptor file format errors"""
    pass


class AudioFileError(AutoDITagError):
    """Exception for audio file related errors"""
    pass


def validate_descriptor_file(file_path: str) -> List[str]:
    """
    Validate the descriptor file format and return list of valid lines.
    Raises DescriptorFileError with detailed information if validation fails.
    """
    if not os.path.exists(file_path):
        raise DescriptorFileError(f"Descriptor file not found: {file_path}")

    if not os.path.isfile(file_path):
        raise DescriptorFileError(f"Path is not a file: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
    except PermissionError:
        raise DescriptorFileError(f"Permission denied reading file: {file_path}")
    except UnicodeDecodeError as e:
        raise DescriptorFileError(f"Unable to decode file {file_path}. Please ensure it's UTF-8 encoded. Error: {e}")
    except Exception as e:
        raise DescriptorFileError(f"Error reading file {file_path}: {e}")

    if not lines:
        raise DescriptorFileError(f"Descriptor file is empty: {file_path}")

    valid_lines = []
    pattern = r'(\d{2})_(.*);\s(.*)\s--\s(.*)$'

    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line:  # Skip empty lines
            continue

        # Check for common formatting mistakes
        if ';' not in line:
            if ',' in line:
                raise DescriptorFileError(
                    f"Line {line_num}: Found comma (,) but expected semicolon (;). "
                    f"Format should be: TRACKNUM_TITLE; ARTIST -- DANCE\n"
                    f"Line content: '{line}'"
                )
            else:
                raise DescriptorFileError(
                    f"Line {line_num}: Missing semicolon (;). "
                    f"Format should be: TRACKNUM_TITLE; ARTIST -- DANCE\n"
                    f"Line content: '{line}'"
                )

        if ' -- ' not in line:
            if ' - ' in line:
                raise DescriptorFileError(
                    f"Line {line_num}: Found single dash (-) but expected double dash (--). "
                    f"Format should be: TRACKNUM_TITLE; ARTIST -- DANCE\n"
                    f"Line content: '{line}'"
                )
            else:
                raise DescriptorFileError(
                    f"Line {line_num}: Missing double dash (--) separator. "
                    f"Format should be: TRACKNUM_TITLE; ARTIST -- DANCE\n"
                    f"Line content: '{line}'"
                )

        # Check if line matches the expected pattern
        match = re.match(pattern, line)
        if not line.startswith(f"{line_num:02d}"):
            expected_prefix = f"{line_num:02d}"
            actual_prefix = line[:3] if len(line) >= 3 else line
            raise DescriptorFileError(
                f"Line {line_num}: Track number mismatch. "
                f"Expected '{expected_prefix}' but found '{actual_prefix}'. "
                f"Each line should start with the zero-padded line number.\n"
                f"Line content: '{line}'"
            )
        if not match:
            # Provide more specific error messages
                # Generic format error
                raise DescriptorFileError(
                    f"Line {line_num}: Invalid format. "
                    f"Expected format: TRACKNUM_TITLE; ARTIST -- DANCE\n"
                    f"Line content: '{line}'"
                )

        valid_lines.append(line)

    if not valid_lines:
        raise DescriptorFileError(f"No valid entries found in descriptor file: {file_path}")

    return valid_lines


def validate_music_directory(dir_path: str) -> None:
    """Validate the music directory exists and contains files"""
    if not os.path.exists(dir_path):
        raise AudioFileError(f"Music directory not found: {dir_path}")

    if not os.path.isdir(dir_path):
        raise AudioFileError(f"Path is not a directory: {dir_path}")

    try:
        files = os.listdir(dir_path)
    except PermissionError:
        raise AudioFileError(f"Permission denied accessing directory: {dir_path}")

    if not files:
        raise AudioFileError(f"Music directory is empty: {dir_path}")


def parse_filename(filename: str) -> Optional[Tuple[str, str, str, str]]:
    """
    Parse a filename and return (track_num, title, artist, dance) or None if invalid.
    """
    pattern = r'(\d{2})_(.*);\s(.*)\s--\s(.*)\.mp3'
    match = re.match(pattern, filename)
    if match:
        return match.groups()
    return None


def create_playlist_files(args: argparse.Namespace):
    """Create M3U playlist files with enhanced error handling"""
    try:
        validate_music_directory(args.dir)

        with open(f'./{args.name}.m3u', 'w', encoding='utf-8') as playlist_file:
            lines = ['#EXTM3U\n']
            sdir = os.listdir(args.dir)
            sdir.sort()

            processed_files = 0
            for af in sdir:
                if not af.endswith('.mp3'):
                    continue

                parsed = parse_filename(af)
                if not parsed:
                    print(f"Warning: Skipping file with invalid name format: {af}")
                    continue

                track_num, title, artist, dance = parsed

                try:
                    relpath = os.path.join(args.dir, af)
                    audio = MP3(relpath)
                    duration = str(int(audio.info.length))
                    lines.append(f"#EXTINF:{duration},{artist} - {title}\n")
                    lines.append(urllib.parse.quote(relpath) + '\n')
                    processed_files += 1
                except Exception as e:
                    print(f"Warning: Could not process audio file {af}: {e}")
                    continue

            if processed_files == 0:
                raise AudioFileError("No valid MP3 files were processed")

            playlist_file.writelines(lines)

        shutil.copy(f'./{args.name}.m3u', f'./{args.name}.m3u8')
        print(f'Created playlist files with {processed_files} tracks')

    except Exception as e:
        if isinstance(e, (AudioFileError, AutoDITagError)):
            raise
        else:
            raise AudioFileError(f"Error creating playlist files: {e}")


def tag(args: argparse.Namespace) -> None:
    """Tag MP3 files with enhanced error handling"""
    try:
        validate_music_directory(args.dir)

        files = [f for f in os.listdir(args.dir) if f.endswith('.mp3')]
        if not files:
            raise AudioFileError(f"No MP3 files found in directory: {args.dir}")

        processed_files = 0
        for f in files:
            parsed = parse_filename(f)
            if not parsed:
                print(f"Warning: Skipping file with invalid name format: {f}")
                continue

            track_num, title, artist, dance = parsed
            try:
                apply_tags(os.path.join(args.dir, f), track_num, title, artist, dance, args.name)
                processed_files += 1
            except Exception as e:
                print(f"Warning: Could not tag file {f}: {e}")
                continue

        if processed_files == 0:
            raise AudioFileError("No files were successfully tagged")

        print(f"Successfully tagged {processed_files} files")

    except Exception as e:
        if isinstance(e, (AudioFileError, AutoDITagError)):
            raise
        else:
            raise AudioFileError(f"Error during tagging process: {e}")


def apply_tags(f: str, num: str, title: str, artist: str, dance: str, album: str) -> None:
    """Apply ID3 tags to an MP3 file with error handling"""
    if not os.path.exists(f):
        raise AudioFileError(f"File not found: {f}")

    try:
        tags = ID3(f)
    except Exception as e:
        raise AudioFileError(f"Could not read ID3 tags from {f}: {e}")

    try:
        tags.delall('COMM')
        tags.delall('TXXX')

        tags.add(TRCK(encode=3, text=num))
        tags.add(TRK(encode=3, text=num))
        tags.add(TIT2(encode=3, text=title))
        tags.add(TPE1(encode=3, text=artist))
        tags.add(TCOM(encode=3, text=artist))
        tags.add(TCON(encode=3, text=dance))
        tags.add(COMM(encode=3, text=dance))
        tags.add(TALB(encode=3, text=album))
        tags.add(TPE2(encode=3, text=album))

        tags.save()
        print(f'Tagged {os.path.basename(f)}')

    except Exception as e:
        raise AudioFileError(f"Could not save tags to {f}: {e}")


def rename(args: argparse.Namespace) -> None:
    """Rename files based on descriptor file with enhanced error handling"""
    try:
        # Validate inputs
        valid_lines = validate_descriptor_file(args.file)
        validate_music_directory(args.dir)

        renamed_count = 0
        missing_files = []

        for count, line in enumerate(valid_lines, 1):
            scount = f"{count:02d}"

            # Find matching files
            matching_files = []
            for f in os.listdir(args.dir):
                if re.match(fr"{scount}[-_].*", f):
                    matching_files.append(f)

            if not matching_files:
                missing_files.append(f"Track {scount}: No file found matching pattern '{scount}_*' or '{scount}-*'")
                continue

            if len(matching_files) > 1:
                print(f"Warning: Multiple files found for track {scount}: {matching_files}")
                print(f"Using: {matching_files[0]}")

            source_path = os.path.join(args.dir, matching_files[0])
            target_path = os.path.join(args.dir, f"{line.strip()}.mp3")

            try:
                if os.path.exists(target_path):
                    print(f"Warning: Target file already exists, skipping: {target_path}")
                    continue

                os.rename(source_path, target_path)
                print(f'Renamed {matching_files[0]} -> {line.strip()}.mp3')
                renamed_count += 1

            except PermissionError:
                print(f"Error: Permission denied renaming {source_path}")
                continue
            except Exception as e:
                print(f"Error renaming {source_path}: {e}")
                continue

        if missing_files:
            print("\nMissing files:")
            for missing in missing_files:
                print(f"  {missing}")

        if renamed_count == 0:
            raise AudioFileError("No files were successfully renamed")

        print(f"\nSuccessfully renamed {renamed_count} files")

    except Exception as e:
        if isinstance(e, (DescriptorFileError, AudioFileError, AutoDITagError)):
            raise
        else:
            raise AutoDITagError(f"Unexpected error during rename process: {e}")


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog='AutoDITag',
        description='Automatically rename and tag your dance playlist',
        epilog='see https://github.com/klassenserver7b/AutoDITag'
    )
    parser.add_argument('-f', '--file', dest='file', required=True, default='./tänze.txt',
                        help='Your txt file containing the playlist')
    parser.add_argument('-d', '--dir', dest='dir', required=True, default='./Tanzmusik',
                        help='The directory of the mp3 files to process')
    parser.add_argument('-n', '--name', dest='name', required=True,
                        help='The name of the Playlist. eg: Schulball 08.05.2024')

    return parser.parse_args()


def main():
    try:
        args = get_args()

        print("AutoDITag - Processing your dance playlist...")
        print(f"Descriptor file: {args.file}")
        print(f"Music directory: {args.dir}")
        print(f"Playlist name: {args.name}")
        print("-" * 50)

        print("\nStep 1: Renaming files...")
        rename(args)

        print("\nStep 2: Tagging files...")
        tag(args)

        print("\nStep 3: Creating playlist files...")
        create_playlist_files(args)

        print("\n" + "=" * 50)
        print("AutoDITag completed successfully!")
        print(f"Created: {args.name}.m3u and {args.name}.m3u8")

    except DescriptorFileError as e:
        print(f"\n❌ Descriptor File Error:")
        print(f"   {e}")
        print(f"\n💡 Expected format for each line:")
        print(f"   TRACKNUM_TITLE; ARTIST -- DANCE")
        print(f"   Example: 01_Voices of Spring; André Rieu -- Wiener Walzer")
        sys.exit(1)

    except AudioFileError as e:
        print(f"\n❌ Audio File Error:")
        print(f"   {e}")
        sys.exit(1)

    except AutoDITagError as e:
        print(f"\n❌ AutoDITag Error:")
        print(f"   {e}")
        sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Unexpected Error:")
        print(f"   {e}")
        print(f"\n🐛 This might be a bug. Please report it at:")
        print(f"   https://github.com/klassenserver7b/AutoDITag/issues")
        sys.exit(1)


if __name__ == "__main__":
    main()