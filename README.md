# Shiro's Spell Inspector

SSI is a free-software tool intended to view spell information of the World of
Warcraft game. It is of similar purpose as the now discontinued Qt Spellworks,
but with different goals. It is written in Python. This is only my second time
using Python for a project, so keep that in mind when haiting on the code
quality... or lack thereof.

The code is licensed under the GNU GENERAL PUBLIC LICENSE Version 3.

# Features

Features of the program:

- Powerful Python driven searching with source-completion for all attributes and
  functions exposed by the SSI framework (see Help inside the program for
  examples of what can be done).
- Parses your source for defines, making the program accept new spell attributes
  as you discover and document them.
- Easy to extend and customize. The UI can be modified with Qt Designer (a
  WYSIWYG UI editor), and the code is all in Python making it easy to modify to
  fit your preferences.

# TODOs

Stuff I want to do but haven't yet:

- Add more data about inspected spells. Such as relations to other spells and
  effect/aura specific understanding of misc values. And more.
- Add more versions.
- Maybe functionality to save code snippets that you find yourself using
  repeatedly?

# Screenshots!

Here's two screenshots of what the program looks like in action:

Scripting:  http://i.imgur.com/mYhV7YI.png
Inspecting: http://i.imgur.com/98E0oFe.png

# Installation

## Windows

### Getting the source

There's two methods to get the source, the recommended is through git. However,
github also provides the ability to download the repo as a zip archive, that you
can unpack. To do the git approach get msysgit from https://msysgit.github.io/
if not installed already. Then open 'Git Bash' and run:

    cd ~
    git clone https://github.com/ccshiro/ssi.git

### Third-party dependencies

Download and install the following:

#### Python3

https://www.python.org/downloads/
Chose a version and click download, get the MSI installer appropriate for your
architecture. In the customize Python part make sure you enable 'Add python.exe
to Path'.

#### PyQt4

http://www.riverbankcomputing.com/software/pyqt/download
Select the binary package for Qt4 for your python version. For example, at the
time of writing you might want: 'PyQt4-4.11.3-gpl-Py3.4-Qt4.8.6-x64.exe'.

### Running the program

To run the program you can double click main.py in the root folder of the
project, or you can open a cmd.exe (or git bash) and type:

    python main.py

The program now needs to be set up for the version you want to use. If you go to
File, Version Menu and select a version number the program will print what files
are missing for that version. You need to resolve those missing files. To do so,
I recommend you either copy all of those files into the given path, or even
better symlink the .dbc files and copy the SharedDefines.h. To symlink the DBCs
run the following (replace what's inside <>):

    cd C:\Users\<UserName>\.ssi
    mkdir "<vers>" && cd "<vers>"
    SET dbcs="<C:\Path\To\DbcFolder>"

All of the following can be copied and run at once:

    mklink Spell.dbc %dbcs%\Spell.dbc && ^
    mklink SpellIcon.dbc %dbcs%\SpellIcon.dbc && ^
    mklink SpellDuration.dbc %dbcs%\SpellDuration.dbc && ^
    mklink SpellRange.dbc %dbcs%\SpellRange.dbc && ^
    mklink SpellRadius.dbc %dbcs%\SpellRadius.dbc && ^
    mklink SpellCastTimes.dbc %dbcs%\SpellCastTimes.dbc

Then manually copy ShareDefines.h from MaNGOS or TrinityCore to the same
directory.

You can now use the program's functionality, however to get exposed to all the
functionality a last, optional, step is required. Please go to the the
'Resolving enums' section in this README for further instructions.

## GNU/Linux

I examplify how to get this running on Debian Jessie here, but the process is
very similiar and easy to adapt to other distros.

Open a terminal and run as root:

    apt-get install git python3 python3-pyqt4

And then as your user:

    cd ~
    git clone https://github.com/ccshiro/ssi.git

## Running the program

In your terminal type:

    ./main.py

The program now needs to be set up for the version you want to use. If you go to
File, Version Menu and select a version number the program will print what files
are missing for that version. You need to resolve those missing files. To do so,
I recommend you either copy all of those files into the given path, or even
better symlink the .dbc files and copy the SharedDefines.h. To symlink the DBCs
run the following (replace what's inside <>):

    cd ~/.ssi
    mkdir "<vers>" && cd "<vers>"
    dbcs="/path/to/dbc/folder"

All of the following can be copied and run at once:

    ln -s "${dbcs}/Spell.dbc" Spell.dbc && \
    ln -s "${dbcs}/SpellIcon.dbc" SpellIcon.dbc && \
    ln -s "${dbcs}/SpellDuration.dbc" SpellDuration.dbc && \
    ln -s "${dbcs}/SpellRange.dbc" SpellRange.dbc && \
    ln -s "${dbcs}/SpellRadius.dbc" SpellRadius.dbc && \
    ln -s "${dbcs}/SpellCastTimes.dbc" SpellCastTimes.dbc 

## OSX

TODO

# Usage

The program should be fairly self-contained. There's a help that documents the
scripting capabilities and has some snippets that might be useful.

# Resolving enums

SSI parses SharedDefines.h for enumerations. However, unfortunately it does not
have all the enums the program uses.  If you look at a spell you will notice
several ${INVALID_ENUM} strings. These are for when the enum was not found in
SharedDefines.h. To resolve this you need to manually copy the enum into
SharedDefines.h (hence why we didn't symlink it earlier). Below are enums
probably missing and where to find them:

## (C)MaNGOS

| Enum                     | File                 |
|-----------------         |----------------------|
|SpellFamily               |DBCEnums.h            |
|AuraType                  |SpellAuraDefines.h    |
|SpellInterruptFlags       |Unit.h                |
|SpellChannelInterruptFlags|Unit.h                |
|SpellAuraInterruptFlags   |Unit.h                |
|SpellCastTargetFlags      |DBCEnums.h            |
|InventoryTypef            |ItemPrototype.h       |
|ItemClass                 |ItemPrototype.h       |
|ItemSubclass*             |ItemPrototype.h       |
|ProcFlags                 |SpellMgr.h            |

\* All 16 of them.

## TrinityCore

TODO
