# PLDGenerator

[![Python](https://img.shields.io/badge/Powered%20by-Python%203.6+-yellow?style=for-the-badge)](https://github.com/d4data-official/d4data-json-pld/releases)

A (super) script to generate EPITECH's EIP Project Log Documents.

## Requirements

You need first to install `inkscape`, `latexmk`, `texlive` and `texlive-latex-extra`.

Json file uses those schema to work : <https://github.com/super-bunny/pld-json-schema>

You have to put a logo.svg file and sublogo.svg file in the assets folder.

## Usage

```bash
./main.py file.json # Generate multiple files with the name file, which one of them file.pdf is the output
./main.py file.json -f # Generate multiple files with the name out, which one of them out.pdf is the output
./clean.sh # Clean all the multiples files generated in the repository
```
