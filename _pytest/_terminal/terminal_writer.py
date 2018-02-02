# -*- coding: utf-8 -*-s
from __future__ import absolute_import, unicode_literals

import six


def flatten(values):
    for x in values:
        if isinstance(x, (list, tuple)):
            for y in flatten(x):
                yield y
        else:
            yield x

class TerminalWriterMixin(object):
    _PROGRESS_LENGTH = len(' [100%]')
    _tw = None
    _session = None
    _show_progress_info = False
    _progress_items_reported = 0
    config = None
    startdir = None

    def write(self, content, **markup):
        self._write(content, **markup)

    def write_line(self, line, ensure_newline=True, **markup):
        if not isinstance(line, six.text_type):
            line = six.text_type(line, errors="replace")
        if ensure_newline:
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
        # line = line.encode('utf-8')
        # fill = fill.encode('utf-8')
        self._write("\r" + str(line) + str(fill), **markup)
        # line = line.encode('utf-8')
        # fill = fill.encode('utf-8')
        # self._write("\r" + line + fill, **markup)


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

    def write_skipped_summary_info(self):
        self._tw.sep("=", self.language.get_skipped_summary_header())

    def _printcollecteditems(self, items):
        # to print out items and their parent collectors
        # we take care to leave out Instances aka ()
        # because later versions are going to get rid of them anyway

        if self._is_more_quiet():
            counts = {}
            for item in items:
                name = item.nodeid.split('::', 1)[0]
                counts[name] = counts.get(name, 0) + 1
            for name, count in sorted(counts.items()):
                self._write_line("%s: %d" % (name, count))

        elif self._is_quiet():
            for item in items:
                nodeid = item.nodeid
                nodeid = nodeid.replace("::()::", "::")
                self._write_line(nodeid)
        else:
            stack = []
            for item in items:
                needed_collectors = item.listchain()[1:]  # strip root node
                while stack:
                    if stack == needed_collectors[:len(stack)]:
                        break
                    stack.pop()
                for col in needed_collectors[len(stack):]:
                    stack.append(col)
                    indent = (len(stack) - 1) * "  "
                    self._write_line("%s%s" % (indent, col))

    def _report_keyboardinterrupt(self, _keyboardinterrupt_memo):
        msg = _keyboardinterrupt_memo.reprcrash.message
        self.write_sep("!", msg)
        if "KeyboardInterrupt" in msg:
            if self.config.option.fulltrace:
                _keyboardinterrupt_memo.toterminal(self._tw)
            else:
                self._write_line(self.language.get_show_traceback_instructions(), yellow=True)
                _keyboardinterrupt_memo.reprcrash.toterminal(self._tw)

    def _write_report_lines_from_hooks(self, lines):
        lines.reverse()
        for line in flatten(lines):
            self.write_line(line)
