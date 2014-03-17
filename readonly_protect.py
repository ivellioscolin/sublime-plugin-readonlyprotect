import sublime, sublime_plugin, sys, os, stat

def DbgPrint(argv):
    global config
    if config.debug_mode:
        print(argv)

def plugin_loaded():
    global manualMode
    manualMode = {}

    settings = sublime.load_settings('readonly_protect.sublime-settings')

    global config

    class config:
        def load(self):
            config.auto_protect = bool(settings.get('auto_protect', True))
            config.debug_mode = bool(settings.get('debug_mode', False))

    config = config()
    config.load()

    settings.add_on_change('reload', lambda:config.load())

    DbgPrint("ReadOnly Protect plugin_loaded")
    DbgPrint("auto protect status is %d" %(config.auto_protect))

if sys.version_info[0] == 2:
    plugin_loaded()

    DbgPrint("Sublime version 2")


class ToggleEditableCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        UpdateManualMode(self.view.id(), True, True)
        if (self.view.is_read_only()):
            self.view.set_read_only(False)
            self.view.set_status('readonly_protect', 'Editable')

            DbgPrint("View %d file %s is set editable" %(self.view.id(), self.view.file_name()))
        else:
            self.view.set_read_only(True)
            self.view.set_status('readonly_protect', 'Uneditable')

            DbgPrint("View %d file %s is set uneditable" %(self.view.id(), self.view.file_name()))
    def is_checked(self, **args):
        if (self.view.is_read_only()):
            return False
        else:
            return True



class ReadonlyProtectEventListener(sublime_plugin.EventListener):
    def on_load(self, view):
        DbgPrint("ReadOnly Protect on_load")
        DbgPrint("View %d on_load" %(view.id()))
        if config.auto_protect:
            DbgPrint("Auto protect mode is ON")
            if view.file_name() != None:
                if not(stat.S_IWUSR & os.stat(view.file_name()).st_mode):
                    UpdateManualMode(view.id(), False, True)
                    view.set_read_only(True)
                    view.set_status('readonly_protect', 'Uneditable')

                    DbgPrint("View %d file %s is set uneditable" %(view.id(),view.file_name()))
                else:
                    DbgPrint("View %d file %s is not readonly" %(view.id(),view.file_name()))
            else:
                DbgPrint("View %d has no file name" %(view.id()))
        else:
            DbgPrint("Auto protect mode is OFF")


    def on_close(self, view):
        DbgPrint("ReadOnly Protect on_close")
        DbgPrint("View %d on_close" %(view.id()))
        if view.file_name() != None:
            UpdateManualMode(view.id(), False, False)


class control_readonly_auto_protect(sublime_plugin.ApplicationCommand):
    def run(self):
        config.auto_protect = not config.auto_protect
        DbgPrint("auto protect status is %d" %(config.auto_protect))

    def is_checked(self, **args):
        if (config.auto_protect):
            return True
        else:
            return False

    #def description(self):
    #    return 'Disable' if config.auto_protect else 'Enable'


def UpdateManualMode(viewId, isManualMode, isSet):
    DbgPrint("ReadOnly Protect UpdateManualMode")
    global manualMode
    if isSet: # Update
        if isManualMode: # Manual toggle mode
            if str(viewId) in manualMode.keys(): # Set only when the file is readonly
                manualMode[str(viewId)] = isManualMode
        else:
            manualMode[str(viewId)] = isManualMode
            DbgPrint("View %d is added to the list." %(viewId))
    else: # Remove
        if str(viewId) in manualMode.keys():
            manualMode.pop(str(viewId))
            DbgPrint("View %d is removed from the list." %(viewId))
