# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from enum import Enum
import six

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


class WriterMixin(object):
    _tw = None

    def write(self, content, **markup):
        self._write(content, **markup)

    def write_line(self, line, **markup):
        if not isinstance(line, six.text_type):
            line = six.text_type(line, errors="replace")
        self._ensure_newline()
        self._write_line(line, **markup)

    def rewrite(self, line, **markup):
        """
        Rewinds the terminal cursor to the beginning and writes the given line.

        :kwarg erase: if True, will also add spaces until the full terminal width to ensure
            previous lines are properly erased.

        The rest of the keyword arguments are markup instructions.
        """
        erase = markup.pop('erase', False)
        if erase:
            fill_count = self._tw.fullwidth - len(line) - 1
            fill = ' ' * fill_count
        else:
            fill = ''
        line = str(line)
        self._write("\r" + line + fill, **markup)



    def _write(self, *args, **kwargs):
        self._tw.write(*args, **kwargs)



    def _write_line(self, *args, **kwargs):
        self._tw.line(*args, **kwargs)