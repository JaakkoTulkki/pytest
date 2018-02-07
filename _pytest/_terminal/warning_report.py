import py

class WarningReport:
    """
    Simple structure to hold warnings information captured by ``pytest_logwarning``.
    """

    def __init__(self, message, nodeid=None, fslocation=None):
        """
        :param code: unused
        :param str message: user friendly message about the warning
        :param str|None nodeid: node id that generated the warning (see ``get_location``).
        :param tuple|py.path.local fslocation:
            file system location of the source of the warning (see ``get_location``).
        """
        self.message = message
        self.nodeid = nodeid
        self.fslocation = fslocation

    def get_location(self, config):
        """
        Returns the more user-friendly information about the location
        of a warning, or None.
        """
        if self.nodeid:
            return self.nodeid
        if self.fslocation:
            if isinstance(self.fslocation, tuple) and len(self.fslocation) >= 2:
                filename, linenum = self.fslocation[:2]
                relpath = py.path.local(filename).relto(config.invocation_dir)
                return '%s:%s' % (relpath, linenum)
            else:
                return str(self.fslocation)
        return None
