from abc import ABCMeta, abstractmethod


class Language(metaclass=ABCMeta):

    @abstractmethod
    def get_show_traceback_instructions(self):
        raise NotImplementedError('Not implemented')

    @abstractmethod
    def get_internal_error(self):
        raise NotImplementedError('Not implemented')

    @abstractmethod
    def get_plugin_registered(self, plugin):
        raise NotImplementedError('Not implemented')

    @abstractmethod
    def get_session_starts(self):
        raise NotImplementedError('Not implemented')

    @abstractmethod
    def get_platform(self):
        raise NotImplementedError('Not implemented')

    @abstractmethod
    def get_colletion_failures(self):
        raise NotImplementedError('Not implemented')

    @abstractmethod
    def get_test_session(self):
        raise NotImplementedError('Not implemented')

    @abstractmethod
    def get_warnings_summary(self):
        raise NotImplementedError('Not implemented')

    @abstractmethod
    def get_undetermined_location(self):
        raise NotImplementedError('Not implemented')

    @abstractmethod
    def get_passes(self):
        raise NotImplementedError('Not implemented')

    @abstractmethod
    def get_failures(self):
        raise NotImplementedError('Not implemented')

    @abstractmethod
    def get_errors(self):
        raise NotImplementedError('Not implemented')

    @abstractmethod
    def get_errors_collecting(self):
        raise NotImplementedError('Not implemented')

    @abstractmethod
    def get_errors_setup(self):
        raise NotImplementedError('Not implemented')

    @abstractmethod
    def get_errors_teardown(self):
        raise NotImplementedError('Not implemented')

    @abstractmethod
    def get_seconds(self):
        raise NotImplementedError('Not implemented')

    @abstractmethod
    def get_tests_deselected(self):
        raise NotImplementedError('Not implemented')

    @abstractmethod
    def build_summary_stats_dict(self):
        """
        required keys "failed passed skipped deselected xfailed xpassed warnings error"
        :return: dict
        """
        raise NotImplementedError('Not implemented')