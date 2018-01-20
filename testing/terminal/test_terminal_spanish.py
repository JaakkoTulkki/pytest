import pytest


class TestProgressSpanish:

    @pytest.fixture
    def many_tests_file(self, testdir):
        testdir.makepyfile(
            test_bar="""
                import pytest
                @pytest.mark.parametrize('i', range(10))
                def test_bar(i): pass
            """,
            test_foo="""
                import pytest
                @pytest.mark.parametrize('i', range(5))
                def test_foo(i): pass
            """,
            test_foobar="""
                import pytest
                @pytest.mark.parametrize('i', range(5))
                def test_foobar(i): pass
            """,
        )

    def test_zero_tests_collected(self, testdir):
        """Some plugins (testmon for example) might issue pytest_runtest_logreport without any tests being
        actually collected (#2971)."""
        testdir.makeconftest("""
        def pytest_collection_modifyitems(items, config):
            from _pytest.runner import CollectReport
            from _pytest.terminal_language.spanish import Spanish
            for node_id in ('nodeid1', 'nodeid2'):
                rep = CollectReport(node_id, 'passed', None, None)
                rep.when = 'passed'
                rep.duration = 0.1
                config.hook.pytest_runtest_logreport(report=rep, language=Spanish())
        """)
        output = testdir.runpytest('--language=es')
        assert 'ZeroDivisionError' not in output.stdout.str()
        output.stdout.fnmatch_lines([
            '=* 2 pasado en *=',
        ])

    def test_verbose(self, many_tests_file, testdir):
        output = testdir.runpytest('--language=es', '-v')
        output.stdout.re_match_lines([
            r'test_bar.py::test_bar\[0\] PASADO \s+ \[  5%\]',
            r'test_foo.py::test_foo\[4\] PASADO \s+ \[ 75%\]',
            r'test_foobar.py::test_foobar\[4\] PASADO \s+ \[100%\]',
        ])