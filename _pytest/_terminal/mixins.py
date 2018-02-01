# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from enum import Enum


class TerminalVerbose(Enum):
    quiet = -1
    default = 0
    verbose = 1


class VerbosityMixin(object):
    verbosity = None

    def _is_verbose(self):
        return self.verbosity >= TerminalVerbose.verbose.value

    def _is_quiet(self):
        return self.verbosity == TerminalVerbose.quiet.value

    def _is_more_quiet(self):
        return self.verbosity < TerminalVerbose.quiet.value

    def _has_default_verbosity(self):
        return self.verbosity == TerminalVerbose.default.value

    def _showheader(self):
        return self._has_default_verbosity() or self._is_verbose()

    def _show_long_test_info(self):
        return self._is_verbose()

    def _show_fs_path(self):
        return self._has_default_verbosity() or self._is_verbose()
