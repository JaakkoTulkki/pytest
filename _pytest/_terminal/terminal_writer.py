# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import six

class TerminalWriter(object):
    _PROGRESS_LENGTH = len(' [100%]')
    _tw = None
    _session = None
    _show_progress_info = False
    _progress_items_reported = 0
    config = None
    startdir = None

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


    def section(self, title, sep="=", **kw):
        self._tw.sep(sep, title, **kw)

    def line(self, msg, **kw):
        self._write_line(msg, **kw)

    def write_sep(self, sep, title=None, **markup):
        self._ensure_newline()
        self._tw.sep(sep, title, **markup)

    def _ensure_newline(self):
        if self.currentfspath:
            self._write_line()
            self.currentfspath = None

    def _write(self, *args, **kwargs):
        self._tw.write(*args, **kwargs)


    def _write_line(self, *args, **kwargs):
        self._tw.line(*args, **kwargs)

    def _write_ensure_prefix(self, prefix, extra="", **kwargs):
        if self.currentfspath != prefix:
            self._write_line()
            self.currentfspath = prefix
            self._write(prefix)
        if extra:
            self._write(extra, **kwargs)
            self.currentfspath = -2
            self._write_progress_information_filling_space()

    def _write_progress_information_filling_space(self):
        if not self._show_progress_info:
            return
        msg = self._get_progress_information_message()
        fill = ' ' * (self._tw.fullwidth - self._tw.chars_on_current_line - len(msg) - 1)
        self.write(fill + msg, cyan=True)

    def write_fspath_result(self, nodeid, res):
        fspath = self.config.rootdir.join(nodeid.split("::")[0])
        if fspath != self.currentfspath:
            if self.currentfspath is not None:
                self._write_progress_information_filling_space()
            self.currentfspath = fspath
            fspath = self.startdir.bestrelpath(fspath)
            self._write_line()
            self._write(fspath + " ")
        self._write(res)

    def _write_progress_if_past_edge(self):
        if not self._show_progress_info:
            return
        last_item = self._progress_items_reported == self._session.testscollected
        if last_item:
            self._write_progress_information_filling_space()
            return

        past_edge = self._tw.chars_on_current_line + self._PROGRESS_LENGTH + 1 >= self._screen_width
        if past_edge:
            msg = self._get_progress_information_message()
            self._write(msg + '\n', cyan=True)

    def _get_progress_information_message(self):
        collected = self._session.testscollected
        if collected:
            progress = self._progress_items_reported * 100 // collected
            return ' [{:3d}%]'.format(progress)
        return ' [100%]'

    def print_teardown_sections(self, rep):
        for secname, content in rep.sections:
            if 'teardown' in secname:
                self._tw.sep('-', secname)
                if content[-1:] == "\n":
                    content = content[:-1]
                self._write_line(content)
