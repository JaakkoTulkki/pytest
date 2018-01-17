from . import Language


class English(Language):
    def get_show_traceback_instructions(self):
        return "to show a full traceback on KeyboardInterrupt use --fulltrace"

    def get_plugin_registered(self, plugin):
        return "PLUGIN registered: %s" % plugin

    def get_internal_error(self):
        return "INTERNALERROR>"
