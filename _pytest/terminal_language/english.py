from . import Language


class English(Language):
    def get_summary_stats(self, line, session_duration):
        return "%s in %.2f %s" % (line, session_duration, self.get_seconds())

    def get_test_result_translation(self, result):
        return result

    def get_item_plural(self):
        return 'items'

    def get_item(self):
        return 'item'

    def get_skipped_lower(self):
        return 'skipped'

    def get_collected(self):
        return 'collected'

    def get_collecting(self):
        return 'collecting'

    def get_error_lower(self):
        return 'error'

    def get_errors_lower(self):
        return 'errors'

    def no_tests_ran(self):
        return "no tests ran"

    def get_summary_stats_translations(self):
        return {'skipped': 'skipped', 'warnings': 'warnings', 'xfailed': 'xfailed', 'xpassed': 'xpassed',
                'failed': 'failed', 'deselected': 'deselected', 'passed': 'passed', 'error': 'error'}

    def get_session_starts(self):
        return "test session starts"

    def get_show_traceback_instructions(self):
        return "to show a full traceback on KeyboardInterrupt use --fulltrace"

    def get_plugin_registered(self, plugin):
        return "PLUGIN registered: %s" % plugin

    def get_internal_error(self):
        return "INTERNALERROR"

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
        return "ERROR at setup of"

    def get_errors_teardown(self):
        return "ERROR at teardown of"

    def get_seconds(self):
        return "seconds"

    def get_tests_deselected(self):
        return 'tests deselected'
