# AutoDITag

A Tool to automatically rename and tag mp3 files

Meant to be used to create playlist files and corresponding tagged mp3 files, that can be used in [DanceInterpreter](https://github.com/Klassenserver7b/Danceinterpreter)

## Installation and Usage

Requires Python 3.6+, mutagen and argparse

### Pip
```sh
pip install auto-di-tag
auto-di-tag -f PATH_TO_DESCRIPTOR_FILE -d PATH_TO_MUSICFOLDER -n PLAYLISTNAME
```

### Manual
```sh
git clone https://github.com/klassenserver7b/AutoDITag.git
cd AutoDITag
pip install -r requirements.txt
python3 auto_di_tag.py -f PATH_TO_DESCRIPTOR_FILE -d PATH_TO_MUSICFOLDER -n PLAYLISTNAME
```

### How to create a descriptorfile
[see Examples](examples/README.md)

## License
This Project is Licensed under the [GNU GENERAL PUBLIC LICENSE Version 3](LICENSE).
Therefore there is NO WARRANTY for anything regarding this code

## Help Menu

```
usage: AutoDITag [-h] -f FILE -d DIR -n NAME

Automatically rename and tag your dance playlist

options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Your txt file containing the playlist
  -d DIR, --dir DIR     The directory of the mp3 files to process
  -n NAME, --name NAME  The name of the Playlist. eg: Schulball 08.05.2024

see https://github.com/klassenserver7b/AutoDITag
```
