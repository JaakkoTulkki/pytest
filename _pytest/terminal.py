""" terminal reporting of the full testing process.

This is a good source for looking at the various reporting hooks.
"""
from __future__ import absolute_import, division, print_function

import platform
import sys
import time

import pluggy
import py
import six

import pytest
from _pytest import nodes
from _pytest.english import English
from _pytest.main import EXIT_OK, EXIT_TESTSFAILED, EXIT_INTERRUPTED, \
    EXIT_USAGEERROR, EXIT_NOTESTSCOLLECTED
from _pytest.spanish import Spanish
from ._terminal.terminal_verbosity import VerbosityMixin
from ._terminal.terminal_writer import TerminalWriterMixin
from ._terminal.warning_report import WarningReport
from ._terminal.terminal_summary import TerminalSummaryMixin


def pytest_addoption(parser):
    group = parser.getgroup("terminal reporting", "reporting", after="general")
    group._addoption('-v', '--verbose', action="count",
                     dest="verbose", default=0, help="increase verbosity."),
    group._addoption('-q', '--quiet', action="count",
                     dest="quiet", default=0, help="decrease verbosity."),
    group._addoption('-r',
                     action="store", dest="reportchars", default='', metavar="chars",
                     help="show extra test summary info as specified by chars (f)ailed, "
                     "(E)error, (s)skipped, (x)failed, (X)passed, "
                     "(p)passed, (P)passed with output, (a)all except pP. "
                     "Warnings are displayed at all times except when "
                     "--disable-warnings is set")
    group._addoption('--disable-warnings', '--disable-pytest-warnings', default=False,
                     dest='disable_warnings', action='store_true',
                     help='disable warnings summary')
    group._addoption('-l', '--showlocals',
                     action="store_true", dest="showlocals", default=False,
                     help="show locals in tracebacks (disabled by default).")
    group._addoption('--tb', metavar="style",
                     action="store", dest="tbstyle", default='auto',
                     choices=['auto', 'long', 'short', 'no', 'line', 'native'],
                     help="traceback print mode (auto/long/short/line/native/no).")
    group._addoption('--fulltrace', '--full-trace',
                     action="store_true", default=False,
                     help="don't cut any tracebacks (default is to cut).")
    group._addoption('--color', metavar="color",
                     action="store", dest="color", default='auto',
                     choices=['yes', 'no', 'auto'],
                     help="color terminal output (yes/no/auto).")
    group._addoption('--language', default='en', choices=['en', 'es'], help='Select language for the terminal')

    parser.addini("console_output_style",
                  help="console output: classic or with additional progress information (classic|progress).",
                  default='progress')

SUCCESS_STATUS = 0
FAILURE_STATUS = 1


class TerminalReporter(VerbosityMixin, TerminalWriterMixin, TerminalSummaryMixin):
    def __init__(self, config, file=None, language=None):
        import _pytest.config
        self.language = get_language(config) if language is None else language()
        self.config = config
        self.verbosity = self.config.getoption('verbose')
        self._numcollected = 0
        self._session = None

        self.stats = {}
        self.startdir = py.path.local()
        if file is None:
            file = sys.stdout
        self._tw = _pytest.config.create_terminal_writer(config, file)
        # self.writer will be deprecated in pytest-3.4
        self.writer = self._tw
        self._screen_width = self._tw.fullwidth
        # file system path
        self.currentfspath = None
        self.reportchars = getreportopt(config)
        self.hasmarkup = self._tw.hasmarkup
        self.isatty = file.isatty()
        self._progress_items_reported = 0


    def _show_progress_info(self):
        return self.config.getini('console_output_style') == 'progress'

    def pytest_internalerror(self, excrepr):
        for line in six.text_type(excrepr).split("\n"):
            self.write_line("%s> %s" % (self.language.get_internal_error(), line))
        return FAILURE_STATUS

    def pytest_logwarning(self, code, fslocation, message, nodeid):
        warnings = self.stats.setdefault("warnings", [])
        warning = WarningReport(fslocation=fslocation,
                                message=message, nodeid=nodeid)
        warnings.append(warning)

    def pytest_plugin_registered(self, plugin):
        if self.config.getoption('traceconfig'):
            # XXX this event may happen during setup/teardown time
            #     which unfortunately captures our output here
            #     which garbles our output if we use self.write_line
            self.write_line(self.language.get_plugin_registered(plugin))

    def pytest_deselected(self, items):
        self.stats.setdefault('deselected', []).extend(items)

    def pytest_runtest_logstart(self, nodeid, location):
        # ensure that the path is printed before the
        # 1st test of a module starts running
        if self._show_long_test_info():
            line = self._locationline(nodeid, *location)
            self._write_ensure_prefix(line, "")
        elif self._show_fs_path():
            fsid = nodeid.split("::")[0]
            self.write_fspath_result(fsid, "")

    def pytest_runtest_logreport(self, report):
        rep = report
        res = self.config.hook.pytest_report_teststatus(report=rep, language=self.language)
        cat, letter, word = res

        if isinstance(word, tuple):
            word, markup = word
        else:
            markup = self._get_logreport_markup(rep)

        self.stats.setdefault(cat, []).append(rep)
        self._tests_ran = True
        if in_setup_or_teardown(letter, word):
            return
        running_xdist = hasattr(rep, 'node')
        self._progress_items_reported += 1
        if self._is_verbose():
            self._write_verbose_logreport(markup, rep, running_xdist, word)
        else:
            self._write_quiet_logreport(letter, rep, running_xdist)

    def _get_logreport_markup(self, rep):
        if rep.passed:
            markup = {'green': True}
        elif rep.failed:
            markup = {'red': True}
        elif rep.skipped:
            markup = {'yellow': True}
        else:
            markup = {}
        return markup

    def _write_quiet_logreport(self, letter, rep, running_xdist):
        if not running_xdist and self._show_fs_path():
            self.write_fspath_result(rep.nodeid, letter)
        else:
            self._write(letter)
        self._write_progress_if_past_edge()

    def _write_verbose_logreport(self, markup, rep, running_xdist, word):
        line = self._locationline(rep.nodeid, *rep.location)
        if not running_xdist:
            self._write_ensure_prefix(line, word, **markup)
        else:
            self._ensure_newline()
            self._write("[%s]" % rep.node.gateway.id)
            if self._show_progress_info():
                self._write(self._get_progress_information_message() + " ", cyan=True)
            else:
                self._write(' ')
            self._write(word, **markup)
            self._write(" " + line)

    def pytest_collection(self):
        if not self.isatty and self._is_verbose():
            self.write(self.language.get_collecting() + " ...", bold=True)

    def pytest_collectreport(self, report):
        if report.failed:
            self.stats.setdefault(self.language.get_error_lower(), []).append(report)
        elif report.skipped:
            self.stats.setdefault(self.language.get_skipped_lower(), []).append(report)
        items = [x for x in report.result if isinstance(x, pytest.Item)]
        self._numcollected += len(items)
        if self.isatty:
            self.report_collect()

    def pytest_collection_modifyitems(self):
        self.report_collect(True)

    @pytest.hookimpl(trylast=True)
    def pytest_sessionstart(self, session):
        self._session = session
        self._sessionstarttime = time.time()
        if not self._showheader():
            return
        self.write_sep("=", self.language.get_session_starts(), bold=True)

        msg = self._get_python_info_msg()
        if self._is_verbose() or self.config.getoption('debug') or self.config.getoption('pastebin'):
            msg += " -- " + str(sys.executable)
        self.write_line(msg)

        lines = self.config.hook.pytest_report_header(
            config=self.config, startdir=self.startdir)
        self._write_report_lines_from_hooks(lines)

    def pytest_report_header(self, config):
        inifile = ""
        if config.inifile:
            inifile = " " + config.rootdir.bestrelpath(config.inifile)
        lines = ["rootdir: %s, inifile:%s" % (config.rootdir, inifile)]
        plugininfo = config.pluginmanager.list_plugin_distinfo()
        if plugininfo:
            lines.append(
                "plugins: %s" % ", ".join(_plugin_nameversions(plugininfo)))
        return lines

    def pytest_collection_finish(self, session):
        if self.config.getoption('collectonly'):
            self._printcollecteditems(session.items)
            if self.stats.get('failed'):
                self._tw.sep("!", self.language.get_colletion_failures())
                for rep in self.stats.get('failed'):
                    rep.toterminal(self._tw)
                return FAILURE_STATUS
            return SUCCESS_STATUS
        lines = self.config.hook.pytest_report_collectionfinish(
            config=self.config, startdir=self.startdir, items=session.items)
        self._write_report_lines_from_hooks(lines)

    @pytest.hookimpl(hookwrapper=True)
    def pytest_sessionfinish(self, exitstatus):
        outcome = yield
        outcome.get_result()
        self._write_line("")
        summary_exit_codes = (
            EXIT_OK, EXIT_TESTSFAILED, EXIT_INTERRUPTED, EXIT_USAGEERROR,
            EXIT_NOTESTSCOLLECTED)
        if exitstatus in summary_exit_codes:
            self.config.hook.pytest_terminal_summary(terminalreporter=self,
                                                     exitstatus=exitstatus)
            self.summary_errors()
            self.summary_failures()
            self.summary_warnings()
            self.summary_passes()
        if exitstatus == EXIT_INTERRUPTED:
            self._report_keyboardinterrupt(self._keyboardinterrupt_memo)
            del self._keyboardinterrupt_memo
        self.summary_deselected()
        self.summary_stats()

    def pytest_keyboard_interrupt(self, excinfo):
        self._keyboardinterrupt_memo = excinfo.getrepr(funcargs=True)

    def pytest_unconfigure(self):
        if hasattr(self, '_keyboardinterrupt_memo'):
            self._report_keyboardinterrupt(self._keyboardinterrupt_memo)

    def _locationline(self, nodeid, fspath, lineno, domain):
        def mkrel(nodeid):
            line = self.config.cwd_relative_nodeid(nodeid)
            if domain and line.endswith(domain):
                line = line[:-len(domain)]
                values = domain.split("[")
                values[0] = values[0].replace('.', '::')  # don't replace '.' in params
                line += "[".join(values)
            return line

        if fspath:
            res = mkrel(nodeid).replace("::()", "")  # parens-normalization
            if nodeid.split("::")[0] != fspath.replace("\\", nodes.SEP):
                res += " <- " + self.startdir.bestrelpath(fspath)
        else:
            res = "[location]"
        return res + " "

    def _get_python_info_msg(self):
        verinfo = platform.python_version()
        msg = "%s %s -- Python %s" % (self.language.get_platform(),
                                      sys.platform, verinfo)
        if hasattr(sys, 'pypy_version_info'):
            msg += get_pypy_version_message()
        msg += ", pytest-%s, py-%s, pluggy-%s" % (
            pytest.__version__, py.__version__, pluggy.__version__)
        return msg

    def _showheader(self):
        return self._has_default_verbosity() or self._is_verbose()

    def _show_long_test_info(self):
        return self._is_verbose()

    def _show_fs_path(self):
        return self._has_default_verbosity() or self._is_verbose()


def _plugin_nameversions(plugininfo):
    values = []
    for plugin, dist in plugininfo:
        # gets us name and version!
        name = '{dist.project_name}-{dist.version}'.format(dist=dist)
        # questionable convenience, but it keeps things short
        if name.startswith("pytest-"):
            name = name[7:]
        # we decided to print python package names
        # they can have more than one plugin
        if name not in values:
            values.append(name)
    return values


def mywriter(reporter):
    def writer(tags, args):
        msg = " ".join(map(str, args))
        reporter.write_line("[traceconfig] " + msg)
    return writer


def get_pypy_version_message():
    verinfo = ".".join(map(str, sys.pypy_version_info[:3]))
    return "[pypy-%s-%s]" % (verinfo, sys.pypy_version_info[3])


def pytest_configure(config):
    config.option.verbose -= config.option.quiet
    reporter = TerminalReporter(config, sys.stdout)
    config.pluginmanager.register(reporter, 'terminalreporter')
    if config.option.debug or config.option.traceconfig:
        config.trace.root.setprocessor("pytest:config", mywriter(reporter))


def getreportopt(config):
    reportopts = ""
    reportchars = config.option.reportchars
    if not config.option.disable_warnings and 'w' not in reportchars:
        reportchars += 'w'
    elif config.option.disable_warnings and 'w' in reportchars:
        reportchars = reportchars.replace('w', '')
    if reportchars:
        for char in reportchars:
            if char not in reportopts and char != 'a':
                reportopts += char
            elif char == 'a':
                reportopts = 'fEsxXw'
    return reportopts


def pytest_report_teststatus(report, language):
    """
    :param report: instance or _pytest.runner.TestReport
    :param language: instance of Language
    :return:
    """
    if report.passed:
        letter = "."
    elif report.skipped:
        letter = "s"
    elif report.failed:
        letter = "F"
    if language is None:
        outcome_result = report.outcome.upper()
    else:
        outcome_result = language.get_test_result_translation(report.outcome).upper()

    return report.outcome, letter, outcome_result


def get_language(config):
    if config.getoption('language') == 'es':
        return Spanish()
    return English()


def in_setup_or_teardown(letter, word):
    return not letter and not word
