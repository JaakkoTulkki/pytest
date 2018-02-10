# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from abc import ABCMeta, abstractmethod


class Language(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_summary_stats(self, line, session_duration):
        raise NotImplementedError('Not implemented')

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
    def get_summary_stats_translations(self):
        """
        return dict that has translations for summary stat line keys
        e.g. {"failed": "fallados"}
        required keys with translations are
        failed passed skipped deselected xfailed xpassed warnings error
        :return: dict
        """
        raise NotImplementedError('Not implemented')

    @abstractmethod
    def no_tests_ran(self):
        raise NotImplementedError('Not implemented')

    @abstractmethod
    def get_error_lower(self):
        raise NotImplementedError('Not implemented')

    @abstractmethod
    def get_errors_lower(self):
        raise NotImplementedError('Not implemented')

    @abstractmethod
    def get_skipped_lower(self):
        raise NotImplementedError('Not implemented')

    @abstractmethod
    def get_collected(self):
        raise NotImplementedError('Not implemented')

    @abstractmethod
    def get_collecting(self):
        raise NotImplementedError('Not implemented')

    @abstractmethod
    def get_item(self):
        raise NotImplementedError('Not implemented')

    @abstractmethod
    def get_item_plural(self):
        raise NotImplementedError('Not implemented')

    @abstractmethod
    def get_test_result_translation(self, result):
        """ result can be "passed", "failed", "skipped"
            return a correct translation for this
        """
        raise NotImplementedError('Not implemented')

    @abstractmethod
    def get_skipped_summary_header(self):
        raise NotImplementedError('Not implemented')
