# ReadOnly Protect v 1.3.0 

### NOTES
With this plugin, you can: 
- Protect read-only file agaisnt input.
- Poll read-only stat from file system in case changed by other application.
- Show read-only status in status bar.

Work for both Sublime Text 2 and 3. 

### INSTALLATION 

- Search "ReadonlyProtect" in [Package Control]. 
- Grab [latest release] and put all files into "{sublime}\Data\Packages\ReadOnlyProtect" 

### USAGE
- Select automatic mode if you would like to sync the stat with the file system.
- Select manual mode if you would like to force editable or readonly.
- Protect mode and polling interval can be set by global settings from Preferences->Package Settings->ReadOnly Protect. 
- Automatic/manual mode and editable/readonly can be toggled from tab, context or menu. 

### REVISION
#### 1.3.0
Add automatic mode to poll stat from file system.
#### 1.2.0 
Fix comma issue on ST2. Add settings in menu.
#### 1.1.0 
Make README.md rendered properly. 
Change command on tab, context menu and main menu to checkbox. 
#### 1.0.0 
Initial version 

[Package Control]: <https://packagecontrol.io/installation>
[latest release]: <https://github.com/ivellioscolin/sublime-plugin-readonlyprotect/releases>