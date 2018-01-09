import sys

from _pytest.terminal import TerminalReporter


def pytest_runtest_setup(item):
    # called for running each test in 'a' directory
    print("setting up", item)

def pytest_configure(config):
    config.option.verbose -= config.option.quiet
    reporter = TerminalReporter(config, sys.stdout)
    config.pluginmanager.register(reporter, 'terminalreportertwo')