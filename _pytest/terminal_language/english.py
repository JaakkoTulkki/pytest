from . import Language


class English(Language):
    def build_summary_stats_dict(self):
        keys = "failed passed skipped deselected xfailed xpassed warnings error".split()
        return {k: k for k in keys}

    def get_session_starts(self):
        return "test session starts"

    def get_show_traceback_instructions(self):
        return "to show a full traceback on KeyboardInterrupt use --fulltrace"

    def get_plugin_registered(self, plugin):
        return "PLUGIN registered: %s" % plugin

    def get_internal_error(self):
        return "INTERNALERROR>"

    def get_platform(self):
        return "platform"

    def get_colletion_failures(self):
        return "collection failures"

    def get_test_session(self):
        return "test session"

    def get_warnings_summary(self):
        return "warnings summary"

    def get_undetermined_location(self):
        return "undetermined location"

    def get_passes(self):
        return "PASSES"

    def get_failures(self):
        return "FAILURES"

    def get_errors(self):
        return "ERRORS"

    def get_errors_collecting(self):
        return "ERROR collecting "

    def get_errors_setup(self):
        return "ERROR at setup of "

    def get_errors_teardown(self):
        return "ERROR at teardown of "

    def get_seconds(self):
        return "seconds"

    def get_tests_deselected(self):
        return 'tests deselected'


