# roku-sublime
Working on creating a Sublime Text build system for Roku projects using Brightscript.

# Usage
There are 4 commands (Cmd + Shift + P) at the moment
1. Roku: Package and Install
2. Roku: Package
3. Roku: Install Package
4. Roku: Uninstall Package

# Installation

* Download and extract to Sublime Text 2/3 Packages folder
	> Windows:  %APPDATA%\Sublime Text 2\Packages
	> Windows:  %APPDATA%\Sublime Text 3\Packages

	> Mac OS X: ~/Library/Application\ Support/Sublime\ Text\ 2/Packages/
	> Mac OS X: ~/Library/Application\ Support/Sublime\ Text\ 3/Packages/

	> Linux:    ~/.config/sublime-text-2/Packages
	> Linux:    ~/.config/sublime-text-3/Packages

# Configuration

Settings can be found under Preferences > Package Settings > Roku

I would recommend opening the default settings and copying them to the user settings, and then modify the user settings.
For the password, you can leave it blank and you will be prompted for the password during each install.

```javascript
{
    "timeout" : 30,
    "boxes" : [
        {
            "name" : "Familyroom",
            "ip"   : "192.168.0.10",
            "user" : "rokudev",
            "pass" : ""
        },
        {
            "name" : "Master Bedroom",
            "ip"   : "192.168.0.11",
            "user" : "rokudev",
            "pass" : ""
        }
    ]
}

```

# Change log
* Created a basic SublimeText Plugin with 3 commands (roku.py)
* Pulled the .sh scripts from original project into the python scripts and tried to keep them platform agnostic.
* Added default/user settings
* Added support for multiple roku boxes
* Removed the replace command (install will do the same thing)
* Added package and install command
* Swap curl out for python library "requests"
* Added authentication support
