import itertools

import time

def getcrashline(rep):
    """
    :param rep: _pytest.runner.TestReport
    :return: crashline
    """
    try:
        return str(rep.longrepr.reprcrash)
    except AttributeError:
        try:
            return str(rep.longrepr)[:50]
        except AttributeError:
            return ""


def build_summary_stats_line(stats, translation_table=None, no_tests_ran='no tests ran'):
    keys = ("failed passed skipped deselected "
            "xfailed xpassed warnings error").split()
    if not translation_table:
        translation_table = {k: k for k in keys}
    unknown_key_seen = False
    # this could be [k for k in stats.keys() if k]
    for key in stats.keys():
        if key not in keys:
            if key:  # setup/teardown reports have an empty key, ignore them
                keys.append(key)
                unknown_key_seen = True
    parts = []
    for key in keys:
        val = stats.get(key, None)
        if val:
            parts.append("%d %s" % (len(val), translation_table.get(key, key)))

    if parts:
        line = ", ".join(parts)
    else:
        line = no_tests_ran

    if 'failed' in stats or 'error' in stats:
        color = 'red'
    elif 'warnings' in stats or unknown_key_seen:
        color = 'yellow'
    elif 'passed' in stats:
        color = 'green'
    else:
        color = 'yellow'

    return (line, color)


class TerminalSummaryMixin(object):

    def summary_warnings(self):
        if self.hasopt("w"):
            all_warnings = self.stats.get("warnings")
            if not all_warnings:
                return

            grouped = itertools.groupby(all_warnings,
                                        key=lambda wr: wr.get_location(self.config))

            self.write_sep("=", self.language.get_warnings_summary(), yellow=True, bold=False)
            for location, warning_records in grouped:
                self._write_line(
                    str(location) or '<%s>' % self.language.get_undetermined_location())
                for w in warning_records:
                    lines = w.message.splitlines()
                    indented = '\n'.join('  ' + x for x in lines)
                    self._write_line(indented)
                self._write_line()
            self._write_line('-- Docs: http://doc.pytest.org/en/latest/warnings.html')

    #
    # summaries for sessionfinish
    #
    def getreports(self, name):
        values = []
        for x in self.stats.get(name, []):
            if not hasattr(x, '_pdbshown'):
                values.append(x)
        return values

    def summary_passes(self):
        if self.config.option.tbstyle != "no":
            if self.hasopt("P"):
                reports = self.getreports('passed')
                if not reports:
                    return
                self.write_sep("=", self.language.get_passes())
                for rep in reports:
                    msg = self._getfailureheadline(rep)
                    self.write_sep("_", msg)
                    self._outrep_summary(rep)

    def summary_errors(self):
        if self.config.option.tbstyle != "no":
            reports = self.getreports('error')
            if not reports:
                return
            self.write_sep("=", self.language.get_errors())
            for rep in self.stats['error']:
                msg = self._getfailureheadline(rep)
                if not hasattr(rep, 'when'):
                    # collect
                    msg = self.language.get_errors_collecting() + msg
                elif rep.when == "setup":
                    msg = self.language.get_errors_setup() + " " + msg
                elif rep.when == "teardown":
                    msg = self.language.get_errors_teardown() + " " + msg
                self.write_sep("_", msg)
                self._outrep_summary(rep)


    def summary_failures(self):
        if self.config.option.tbstyle != "no":
            reports = self.getreports('failed')
            if not reports:
                return
            self.write_sep("=", self.language.get_failures())
            for rep in reports:
                if self.config.option.tbstyle == "line":
                    line = getcrashline(rep)
                    self.write_line(line)
                else:
                    msg = self._getfailureheadline(rep)
                    markup = {'red': True, 'bold': True}
                    self.write_sep("_", msg, **markup)
                    self._outrep_summary(rep)
                    for report in self.getreports(''):
                        if report.nodeid == rep.nodeid and report.when == 'teardown':
                            self.print_teardown_sections(report)

    def summary_stats(self):
        session_duration = time.time() - self._sessionstarttime
        (line, color) = build_summary_stats_line(self.stats, self.language.get_summary_stats_translations(),
                                                 self.language.no_tests_ran())
        msg = self.language.get_summary_stats(line, session_duration)
        markup = {color: True, 'bold': True}

        if self._has_default_verbosity() or self._is_verbose():
            self.write_sep("=", msg, **markup)
        if self._is_quiet():
            self.write_line(msg, **markup)

    def summary_deselected(self):
        if 'deselected' in self.stats:
            self.write_sep("=", "%d %s" % (
                len(self.stats['deselected']),
                self.language.get_tests_deselected()
            ), bold=True)

    def report_collect(self, final=False):
        if self._is_quiet():
            return

        errors = len(self.stats.get('error', []))
        skipped = len(self.stats.get('skipped', []))
        if final:
            line = self.language.get_collected() + " "
        else:
            line = self.language.get_collecting() + " "

        line += str(self._numcollected) + " " + (
            self.language.get_item() if self._numcollected == 1 else self.language.get_item_plural())
        if errors:
            line += " / %d %s" % (errors, self.language.get_errors_lower())
        if skipped:
            line += " / %d %s" % (skipped, self.language.get_skipped_lower())
        if self.isatty:
            self.rewrite(line, bold=True, erase=True)
            if final:
                self.write('\n')
        else:
            self.write_line(line)

    def _getfailureheadline(self, rep):
        if hasattr(rep, 'location'):
            fspath, lineno, domain = rep.location
            return domain
        else:
            return self.language.get_test_session()  # XXX?

    def hasopt(self, char):
        char = {'xfailed': 'x', 'skipped': 's'}.get(char, char)
        return char in self.reportchars

    def _outrep_summary(self, rep):
        rep.toterminal(self._tw)
        for secname, content in rep.sections:
            self._tw.sep("-", secname)
            if content[-1:] == "\n":
                content = content[:-1]
            self._write_line(content)
