# CreativePython

CreativePython is a Python-based software environment for learning and developing algorithmic art projects.  It mirrors the [JythonMusic API](https://jythonmusic.me/api-reference/), and is powered by [PySide6](https://wiki.qt.io/Qt_for_Python) and [portaudio](http://portaudio.com/).

CreativePython is distributed under the MIT License.

- [Homepage](https://jythonmusic.me/)
- [Download All Examples [ZIP]](https://www.dropbox.com/scl/fo/rvc8m8pt4m0281qn0t4oi/AO2Y0W2qOrOcurlQmLa7M54?rlkey=0sf80bmov135tc85dk9k7ats6&dl=1)
- [Report a Bug (email link)](mailto:creativepythoncofc@gmail.com&subject=[CreativePython]%20Bug%20Report&body=CreativePython%20Version:%20(e.g.%200.1.8)%0D%0AOperating%20System:%20(e.g.%20macOS%2015,%20Windows%2011,%20Ubuntu%2024.04)%0D%0APython%20Version:%20(e.g.%203.11)%0D%0A%0D%0ASummary:%0D%0A%0D%0ASteps%20to%20Reproduce:%0D%0A1.%20%0D%0A2.%20%0D%0A3.%20%0D%0A%0D%0AExpected%20Result:%0D%0A%0D%0AActual%20Result:%0D%0A%0D%0AError%20Messages%20or%20Logs:%0D%0A)
- [Request a Feature (email link)](mailto:creativepythoncofc@gmail.com&subject=[CreativePython]%20Feature%20Request&body=CreativePython%20Version:%20(e.g.%200.1.8)%0D%0AOperating%20System:%20(e.g.%20macOS%2015,%20Windows%2011,%20Ubuntu%2024.04)%0D%0A%0D%0AFeature%20Name:%0D%0A%0D%0ADescription:%0D%0A%0D%0AExample%20Use%20Case%20or%20Scenario:%0D%0A%0D%0ARelated%20Modules%20or%20Functions:%0D%0A%0D%0A)

This package is still under development.

# Requirements

Before installing CreativePython, you will need:

- **Python3**, version 3.9 or greater [[Download](https://www.python.org/downloads/)]
- **A C++ compiler** (see **Troubleshooting** below)

# Installation

If you're familiar with Python development, we recommend installing CreativePython through the Command Prompt/Terminal.

## Windows

Install CreativePython using `pip`:

```
python -m pip install CreativePython
```

## MacOS

Use [Homebrew](https://brew.sh/) to install the prerequisite [portaudio](http://portaudio.com/) library, then install CreativePython using `pip`:

```
brew install portaudio
pip install CreativePython
```

## Linux

Use apt, or your preferred package manager, to install the prerequisite [portaudio](http://portaudio.com/) library, then install CreativePython using `pip`:

```
sudo apt-get portaudio
pip install CreativePython
```

# Using CreativePython

## Importing Libraries

CreativePython's core modules are the `music`, `gui`, `image`, `timer`, `osc`, and `midi` libraries.  You can import these libraries into your python code using:

```
import music
from music import *
from music import Note, Play, C4, HN
```

Or a similar statement.  CreativePython includes a number of useful constants, so we recommend using wildcard imports like `from music import *`.

**NOTE:** The first time you import `music`, CreativePython will download a high-quality soundfont (FluidR3 G2-2.sf2) for you.  You should only have to do this once.

## Running CreativePython programs

CreativePython is designed for use in Python's Interactive Mode.  To use Interactive Mode, enter a command like:

```
python -i <filename>.py
```

## Example

Download [playNote.py](https://www.dropbox.com/scl/fi/z6rkjy4xnofmg0t899se3/playNote.py?rlkey=o3t8c91ne6agj2lqf2aupl8m5&dl=1):

```
# playNote.py
# Demonstrates how to play a single note.
 
from music import *        # import music library
 
note = Note(C4, HN)        # create a middle C half note
Play.midi(note)            # and play it!
```

In IDLE, you can open playNote.py, and select **Run**, then **Run Module** from the toolbar.

In a terminal, run playNote.py in interactive mode:

```
python -i playNote.py
```

After you do, you should hear a single C4 half-note.

## Troubleshooting

### CMake configuration failed

Some of CreativePython's libraries may need to compile C++ code during installation.

- On Windows, download and install [Visual Studio Build Tools 2022](https://visualstudio.microsoft.com/downloads/).  In the Visual Studio installer, make sure "Desktop Development with C++" is checked.

- On MacOS, you can download and install [XCode from the App Store](https://apps.apple.com/us/app/xcode/id497799835?mt=12).

Restart your computer, then try installing CreativePython again.

# PENCIL Editor

CreativePython will soon be available as PENCIL, a customized Python IDE based on IDLE (Python's Integrated Development and Learning Environment).

## Attribution

PENCIL is derived from IDLE, which is part of Python and created by Guido van Rossum and the Python development team. IDLE is distributed under the Python Software Foundation License Version 2.

**Original IDLE Credits:**
- Copyright © 2001-2023 Python Software Foundation. All Rights Reserved.
- See `resources/pencillib/CREDITS.txt` for complete IDLE contributor list.

**PENCIL Modifications:**
- Copyright © 2025 Dr. Bill Manaris
- Modified for use with CreativePython
- Includes custom "JEM" theme and keymap defaults
- User configuration stored in `~/.pencilrc/`

## Licenses

- **CreativePython**: MIT License (see `LICENSE`)
- **IDLE/PENCIL**: Python Software Foundation License Version 2 (see `LICENSE-PSF.txt`)

For complete licensing information, see the `LICENSE` and `LICENSE-PSF.txt` files in this distribution.