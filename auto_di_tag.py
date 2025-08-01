import argparse
import re
import os
import shutil
import urllib.parse
from mutagen.id3 import ID3, TIT2, TALB, TRCK, TRK, TPE1, TPE2, TCON, TCOM, COMM
from mutagen.mp3 import MP3


def create_playlist_files(args: argparse.Namespace):
    with open(f'./{args.name}.m3u', 'w') as playlist_file:
        lines = ['#EXTM3U\n']
        sdir = os.listdir(args.dir)
        sdir.sort()
        for af in sdir:
            groups = re.match(r'(\d{2})_(.*);\s(.*)\s--\s(.*)\.mp3', af).groups()

            relpath = os.path.join(args.dir, af)
            audio = MP3(relpath)
            lines.append(f"#EXTINF:{str(audio.info.length).split('.')[0]},{groups[2]} - {groups[1]}\n")
            lines.append(urllib.parse.quote(relpath)+'\n')

        playlist_file.writelines(lines)
    shutil.copy(f'./{args.name}.m3u', f'./{args.name}.m3u8')
    print('Created playlist files')


def tag(args: argparse.Namespace) -> None:
    for f in os.listdir(args.dir):
        matches = re.match(r'(\d{2})_(.*);\s(.*)\s--\s(.*)\.mp3', f)
        print(f)
        groups = matches.groups()
        apply_tags(os.path.join(args.dir, f), groups[0], groups[1], groups[2], groups[3], args.name)


def apply_tags(f: str, num: str, title: str, artist: str, dance: str, album: str) -> None:
    tags = ID3(f)

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

    print(f'Tagged {f}')


def rename(args: argparse.Namespace) -> None:
    with open(args.file, "r") as file:
        for count, line in enumerate(file, 1):
            scount = str(count)
            if len(scount) == 1:
                scount = "0" + scount

            filep = [f for f in os.listdir(args.dir) if re.match(fr"{scount}[-_].*", f)]
            if filep:
                filep = os.path.join(args.dir, filep[0])
                targetp = os.path.join(args.dir, f"{line.strip()}.mp3")
                print(f'Renamed {filep} to {targetp}')
                os.rename(filep, targetp)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog='AutoDITag',
        description='Automatically rename and tag your dance playlist',
        epilog='see https://github.com/klassenserver7b/AutoDITag'
    )
    parser.add_argument('-f', '--file', dest='file', required=True, default='./tänze.txt',
                        help='Your txt file containing '
                             'the playlist')
    parser.add_argument('-d', '--dir', dest='dir', required=True, default='./Tanzmusik',
                        help='The directory of the mp3 files to process')
    parser.add_argument('-n', '--name', dest='name', required=True,
                        help='The name of the Playlist. eg: Schulball 08.05.2024')

    return parser.parse_args()


def main():
    rename(get_args())
    tag(get_args())
    create_playlist_files(get_args())


if __name__ == "__main__":
    main()
