import sublime, sublime_plugin, sys, os, stat, time

def DbgPrint(argv):
    settings = sublime.load_settings('readonly_protect.sublime-settings')
    if bool(settings.get('debug_mode', False)):
        timestamp = time.strftime("%H:%M:%S - ", time.localtime())
        print(timestamp + argv)

class ViewStatusItem:
    def __init__(self):
        self.view = None
        self.protectMode = None
        self.modeStr = None
        self.isReadOnly = None
        self.readonlyStr = None

class PluginConfig:
    def __init__(self):
        self.protect_mode = 0
        self.polling_interval = 1000
    def load(self):
        settings = sublime.load_settings('readonly_protect.sublime-settings')
        self.protect_mode = int(settings.get('protect_mode', 1))
        self.polling_interval = int(settings.get('polling_interval', 1000))

def DumpAll():
    global viewStatusDict
    DbgPrint("ReadOnly Protect: Dump all start")
    for k in viewStatusDict.keys():
        DbgPrint("ReadOnly Protect: View %s, protect mode: %d %s, readonly mode: %d, %s " %(k, viewStatusDict[k].protectMode, viewStatusDict[k].modeStr, viewStatusDict[k].isReadOnly, viewStatusDict[k].readonlyStr))
    DbgPrint("ReadOnly Protect: Dump all end")

def GetModeString(mode):
    if(mode == 1):
        return 'Auto mode'
    elif(mode == 2):
        return 'Manual mode'
    return 'No protect'

def GetReadonlyString(status):
    if(status):
        return 'Readonly'
    else:
        return 'Editable'

def GetViewModeStatus(view):
    global viewStatusDict
    if str(view.id()) in viewStatusDict.keys():
        return viewStatusDict[str(view.id())]
    else:
        return None

def UpdateViewModeStatus(view, mode, status):
    global viewStatusDict, autoRefCount
    item = ViewStatusItem()
    item.view = view
    item.protectMode = mode
    item.isReadOnly = status
    item.modeStr = GetModeString(mode)
    item.readonlyStr = GetReadonlyString(status)
    if str(view.id()) in viewStatusDict.keys(): # Update an existing view
        if((mode == 1) and (viewStatusDict[str(view.id())].protectMode != 1)):
            autoRefCount = autoRefCount + 1
        elif((viewStatusDict[str(view.id())].protectMode == 1) and (mode != 1)):
            autoRefCount = autoRefCount - 1
        viewStatusDict[str(view.id())].protectMode = item.protectMode
        viewStatusDict[str(view.id())].modeStr = item.modeStr
        viewStatusDict[str(view.id())].isReadOnly = item.isReadOnly
        viewStatusDict[str(view.id())].readonlyStr = item.readonlyStr
    else: # Add a newly added view
        viewStatusDict[str(view.id())] = item
        if(mode == 1):
            autoRefCount = autoRefCount + 1
    view.set_read_only(item.isReadOnly)
    view.set_status('readonly_protect', item.readonlyStr)
    
    DbgPrint("ReadOnly Protect: UpdateViewModeStatus, view %d file %s is updated as: %s, %s" %(view.id(), view.file_name(), item.modeStr, item.readonlyStr))

def RemoveViewModeStatus(view):
    global viewStatusDict, autoRefCount
    if str(view.id()) in viewStatusDict.keys():
        if(viewStatusDict[str(view.id())].protectMode == 1):
            autoRefCount = autoRefCount - 1
        viewStatusDict.pop(str(view.id()))
        DbgPrint("ReadOnly Protect: RemoveViewModeStatus, view %d is removed." %(view.id()))

def isFileReadonly(view):
    isReadonly = False
    if view.file_name() != None:
        if(os.access(view.file_name(), os.F_OK)):
            if not(stat.S_IWUSR & os.stat(view.file_name()).st_mode):
                isReadonly = True
    return isReadonly

def enable_polling(enable):
    global polling_on
    polling_on = enable

def is_polling_enabled():
    global polling_on
    DbgPrint("Polling enablement %d." %(polling_on))
    return polling_on

def start_polling():
    if(not is_polling_enabled()):
        DbgPrint("ReadOnly Protect: start_polling")
        enable_polling(True)
        poll_thread()
    else:
        DbgPrint("ReadOnly Protect: polling thread already started")

def stop_polling():
    DbgPrint("ReadOnly Protect: stop_polling")
    enable_polling(False)

def poll_thread():
    global autoRefCount
    # Enable polling if global mode is auto, or single view is set as auto
    if(is_polling_enabled() and (autoRefCount > 0)):
        DbgPrint("ReadOnly Protect: poll_thread running")
        global viewStatusDict, config
        for k in viewStatusDict.keys():
            if(viewStatusDict[k].protectMode == 1):# Only poll view set as auto
                UpdateViewModeStatus(viewStatusDict[k].view, viewStatusDict[k].protectMode, isFileReadonly(viewStatusDict[k].view))
        sublime.set_timeout(lambda: poll_thread(), config.polling_interval)
    else:
        DbgPrint("ReadOnly Protect: poll_thread stop")
        enable_polling(False)

class ShowDisabledStatusCommand(sublime_plugin.TextCommand):
    def is_visible(self, **args):
        global config
        if(config.protect_mode == 0):
            return True
        else:
            return False

    def is_enabled(self, **args):
        return False

class ToggleProtectModeCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        item = GetViewModeStatus(self.view)
        if(item.protectMode == 1):
            UpdateViewModeStatus(self.view, 2, item.isReadOnly)
            DbgPrint("View %d, protect mode %d" %(item.view.id(), 2))
        elif(item.protectMode == 2):
            UpdateViewModeStatus(self.view, 1, item.isReadOnly)
            sublime.set_timeout(lambda: start_polling(), 1000)
            DbgPrint("View %d, protect mode %d" %(item.view.id(), 1))

    def is_visible(self, **args):
        global config
        if(config.protect_mode == 0):# Do not show this menu if global mode is 0
            return False
        else:
            return True

    def is_enabled(self, **args):
        global config
        if(config.protect_mode == 0):# Disable the control if global mode is 0
            return False
        else:
            return True

    def is_checked(self, **args):
        item = GetViewModeStatus(self.view)
        if ((item != None) and (item.protectMode == 1)):# Show per-view mode
            return True
        else:
            return False

    def description(self):
        if sys.platform == 'win32':
            return 'Automatic'
        else:
            item = GetViewModeStatus(self.view)
            if item != None:
                if item.protectMode == 0:
                    return 'Disabled'
                elif item.protectMode == 1:
                    return 'Auto Mode'
                else:
                    return 'Manual Mode'
            else:
                return 'Automatic'

class ToggleReadonlyCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        if (self.view.is_read_only()):
            UpdateViewModeStatus(self.view, 2, False)
        else:
            UpdateViewModeStatus(self.view, 2, True)
        DbgPrint("View %d is readonly %d" %(self.view.id(), self.view.is_read_only()))

    def is_visible(self, **args):
        global config
        if(config.protect_mode == 0):# Do not show this menu if global mode is 0
            return False
        else:
            return True

    def is_enabled(self, **args):
        item = GetViewModeStatus(self.view)
        if((item != None) and (item.protectMode == 2)):# Only enable the control in manual mode
            return True
        else:
            return False

    def is_checked(self, **args):
        if (self.view.is_read_only()):
            return False
        else:
            return True

    def description(self):
        if sys.platform == 'win32':
            return 'Editable'
        else:
            if self.view.is_read_only():
                return 'Readonly'
            else:
                return 'Editable'

class ReadonlyProtectEventListener(sublime_plugin.EventListener):
    def on_new(self, view):
        DbgPrint("ReadOnly Protect: on_new of view %d" %(view.id()))
        global config
        UpdateViewModeStatus(view, config.protect_mode, False)
        DumpAll()

    def on_load(self, view):
        DbgPrint("ReadOnly Protect: on_load of view %d" %(view.id()))
        global config
        UpdateViewModeStatus(view, config.protect_mode, isFileReadonly(view))
        if(config.protect_mode == 1):
            sublime.set_timeout(lambda: start_polling(), 1000)
        DumpAll()

    def on_close(self, view):
        DbgPrint("ReadOnly Protect: on_close of view %d" %(view.id()))
        RemoveViewModeStatus(view)
        DumpAll()

def init_config():
    global viewStatusDict, config, autoRefCount

    # Reload config if plug-in or setting reloaded
    config = PluginConfig()
    config.load()

    # Stop polling thread
    stop_polling()

    # Start polling if global protect mode is auto
    if(config.protect_mode == 1):
        sublime.set_timeout(lambda: start_polling(), 1000)

    DbgPrint("ReadOnly Protect: init_config, global protect mode is %d" %(config.protect_mode))

def plugin_loaded():
    settings = sublime.load_settings('readonly_protect.sublime-settings')
    settings.add_on_change('reload', lambda:init_config())

    global viewStatusDict, autoRefCount
    viewStatusDict = {}
    autoRefCount = 0

    if(sublime.active_window() != None):
        for view in sublime.active_window().views():
            UpdateViewModeStatus(view, int(settings.get('protect_mode', 1)), isFileReadonly(view))
    init_config()

    DbgPrint("ReadOnly Protect: plugin_loaded")

if sys.version_info[0] == 2:
    plugin_loaded()

    DbgPrint("Sublime version 2")
