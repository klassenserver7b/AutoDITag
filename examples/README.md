## File Structure
A descriptorfile for AutoDITag is pretty simple.

In every line you have one song structured as

`%TRACKNUM%_%TITLE%; %ARTIST% -- %DANCE%`
[see example](tänze.txt)

## Usage

This could be used with:
```
auto-di-tag -f "./tänze.txt" -d "./Tanzmusik" -n "Schulball DD.MM.YYYY"
```
