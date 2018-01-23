# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import sys
import pluggy
import py

import _pytest
import pytest
from _pytest.terminal import TerminalReporter, build_summary_stats_line
from _pytest.spanish import Spanish


class Option(object):
    def __init__(self, verbose=False, fulltrace=False):
        self.verbose = verbose
        self.fulltrace = fulltrace

    @property
    def args(self):
        values = []
        if self.verbose:
            values.append('-v')
        if self.fulltrace:
            values.append('--fulltrace')
        return values


def pytest_generate_tests(metafunc):
    if "option" in metafunc.fixturenames:
        metafunc.addcall(id="default",
                         funcargs={'option': Option(verbose=False)})
        metafunc.addcall(id="verbose",
                         funcargs={'option': Option(verbose=True)})
        metafunc.addcall(id="quiet",
                         funcargs={'option': Option(verbose=-1)})
        metafunc.addcall(id="fulltrace",
                         funcargs={'option': Option(fulltrace=True)})


class TestTerminal(object):
    def test_pass_skip_fail(self, testdir, option):
        testdir.makepyfile("""
            import pytest
            def test_ok():
                pass
            def test_skip():
                pytest.skip("xx")
            def test_func():
                assert 0
        """)
        result = testdir.runpytest('--language=es', *option.args)
        if option.verbose:
            result.stdout.fnmatch_lines([
                "*test_pass_skip_fail.py::test_ok PASADO*",
                "*test_pass_skip_fail.py::test_skip OMITIDO*",
                "*test_pass_skip_fail.py::test_func FALLADO*",
            ])
        else:
            result.stdout.fnmatch_lines([
                "*test_pass_skip_fail.py .sF*"
            ])
        result.stdout.fnmatch_lines([
            "    def test_func():",
            ">       assert 0",
            "E       assert 0",
        ])

    def test_internalerror(self, testdir, linecomp):
        modcol = testdir.getmodulecol("def test_one(): pass")
        modcol.config.option.language = 'es'
        rep = TerminalReporter(modcol.config, file=linecomp.stringio)
        excinfo = pytest.raises(ValueError, "raise ValueError('hello')")
        rep.pytest_internalerror(excinfo.getrepr())
        linecomp.assert_contains_lines([
            "ERROR INTERNO> *ValueError*hello*"
        ])

    def test_itemreport_subclasses_show_subclassed_file(self, testdir):
        testdir.makepyfile(test_p1=str("""
            class BaseTests(object):
                def test_p1(self):
                    pass
            class TestClass(BaseTests):
                pass
        """))
        p2 = testdir.makepyfile(test_p2=str("""
            from test_p1 import BaseTests
            class TestMore(BaseTests):
                pass
        """))
        result = testdir.runpytest('--language=es', p2)
        result.stdout.fnmatch_lines([
            "*test_p2.py*",
            "*1 pasado*",
        ])
        result = testdir.runpytest("-v", '--language=es', p2)
        result.stdout.fnmatch_lines([
            "*test_p2.py::TestMore::test_p1* <- *test_p1.py*PASADO*",
        ])

    def test_itemreport_directclasses_not_shown_as_subclasses(self, testdir):
        a = testdir.mkpydir("a123")
        a.join("test_hello123.py").write(_pytest._code.Source("""
            class TestClass(object):
                def test_method(self):
                    pass
        """))
        result = testdir.runpytest("--language=es", "-v")
        assert result.ret == 0
        result.stdout.fnmatch_lines([
            "*a123/test_hello123.py*PASADO*",
        ])
        assert " <- " not in result.stdout.str()

    def test_keyboard_interrupt(self, testdir, option):
        testdir.makepyfile("""
            def test_foobar():
                assert 0
            def test_spamegg():
                import py; pytest.skip('skip me please!')
            def test_interrupt_me():
                raise KeyboardInterrupt   # simulating the user
        """)

        result = testdir.runpytest('--language=es', *option.args, no_reraise_ctrlc=True)
        result.stdout.fnmatch_lines([
            "    def test_foobar():",
            ">       assert 0",
            "E       assert 0",
            "*_keyboard_interrupt.py:6: KeyboardInterrupt*",
        ])
        if option.fulltrace:
            result.stdout.fnmatch_lines([
                "*raise KeyboardInterrupt   # simulating the user*",
            ])
        else:
            result.stdout.fnmatch_lines([
                "usa --fulltrace para mostrar un rastreo completo con KeyboardInterrupt"
            ])
        result.stdout.fnmatch_lines(['*KeyboardInterrupt*'])

    def test_collect_single_item(self, testdir):
        """Use singular 'item' when reporting a single test item"""
        testdir.makepyfile("""
            def test_foobar():
                pass
        """)
        result = testdir.runpytest('--language=es')
        result.stdout.fnmatch_lines([u'coleccionado 1 ítem'])

    def test_collect_multiple_items(self, testdir):
        """Use plural 'item' when reporting a single test item"""
        testdir.makepyfile("""
            def test_foobar():
                pass

            def test_barfoo():
                pass
        """)
        result = testdir.runpytest('--language=es')
        result.stdout.fnmatch_lines(['coleccionado 2 ítems'])


class TestCollectonly(object):
    def test_collectonly_skipped_module(self, testdir):
        testdir.makepyfile("""
            import pytest
            pytest.skip("hello")
        """)
        result = testdir.runpytest('--language=es', "--collect-only", "-rs")
        result.stdout.fnmatch_lines([
            "*ERROR en la colección*",
        ])

    def test_collectonly_failed_module(self, testdir):
        testdir.makepyfile("""raise ValueError(0)""")
        result = testdir.runpytest('--language=es', "--collect-only")
        result.stdout.fnmatch_lines([
            "*raise ValueError*",
            "*1 error*",
        ])

    def test_collectonly_fatal(self, testdir):
        testdir.makeconftest("""
            def pytest_collectstart(collector):
                assert 0, "urgs"
        """)
        result = testdir.runpytest('--language=es', "--collect-only")
        result.stdout.fnmatch_lines([
            "*INTERNO*args*"
        ])
        assert result.ret == 3


class TestFixtureReporting(object):
    def test_setup_fixture_error(self, testdir):
        testdir.makepyfile("""
            def setup_function(function):
                print ("setup func")
                assert 0
            def test_nada():
                pass
        """)
        result = testdir.runpytest('--language=es')
        result.stdout.fnmatch_lines([
            "*ERROR en la preparación de test_nada*",
            "*setup_function(function):*",
            "*setup func*",
            "*assert 0*",
            "*1 error*",
        ])
        assert result.ret != 0

    def test_teardown_fixture_error(self, testdir):
        testdir.makepyfile("""
            def test_nada():
                pass
            def teardown_function(function):
                print ("teardown func")
                assert 0
        """)
        result = testdir.runpytest('--language=es')
        result.stdout.fnmatch_lines([
            "*ERROR en el desmontaje de*",
            "*teardown_function(function):*",
            "*assert 0*",
            "*Captured stdout*",
            "*teardown func*",
            "*1 pasado*1 error*",
        ])

    def test_teardown_fixture_error_and_test_failure(self, testdir):
        testdir.makepyfile("""
            def test_fail():
                assert 0, "failingfunc"

            def teardown_function(function):
                print ("teardown func")
                assert False
        """)
        result = testdir.runpytest('--language=es')
        result.stdout.fnmatch_lines([
            "*ERROR en el desmontaje de test_fail*",
            "*teardown_function(function):*",
            "*assert False*",
            "*Captured stdout*",
            "*teardown func*",

            "*test_fail*",
            "*def test_fail():",
            "*failingfunc*",
            "*1 fallado*1 error*",
        ])


class TestTerminalFunctional(object):
    def test_deselected(self, testdir):
        testpath = testdir.makepyfile("""
                def test_one():
                    pass
                def test_two():
                    pass
                def test_three():
                    pass
           """
                                      )
        result = testdir.runpytest('--language=es', "-k", "test_two:", testpath)
        result.stdout.fnmatch_lines([
            "*test_deselected.py ..*",
            "=* 1 pruebas*deseleccionadas *=",
        ])
        assert result.ret == 0

    def test_passes(self, testdir):
        p1 = testdir.makepyfile("""
            def test_passes():
                pass
            class TestClass(object):
                def test_method(self):
                    pass
        """)
        old = p1.dirpath().chdir()
        try:
            result = testdir.runpytest('--language=es')
        finally:
            old.chdir()
        result.stdout.fnmatch_lines([
            "test_passes.py ..*",
            "* 2 pasado*",
        ])
        assert result.ret == 0

    def test_header_trailer_info(self, testdir):
        testdir.makepyfile("""
            def test_passes():
                pass
        """)
        result = testdir.runpytest('--language=es')
        verinfo = ".".join(map(str, sys.version_info[:3]))
        result.stdout.fnmatch_lines([
            "*===== comienza la sesión de prueba ====*",
            "plataforma %s -- Python %s*pytest-%s*py-%s*pluggy-%s" % (
                sys.platform, verinfo,
                pytest.__version__, py.__version__, pluggy.__version__),
            "*test_header_trailer_info.py .*",
            "=* 1 pasado*en *.[0-9][0-9] segundos *=",
        ])

    def test_verbose_reporting(self, testdir, pytestconfig):
        p1 = testdir.makepyfile("""
            import pytest
            def test_fail():
                raise ValueError()
            def test_pass():
                pass
            class TestClass(object):
                def test_skip(self):
                    pytest.skip("hello")
            def test_gen():
                def check(x):
                    assert x == 1
                yield check, 0
        """)
        result = testdir.runpytest('--language=es', p1, '-v')
        result.stdout.fnmatch_lines([
            "*test_verbose_reporting.py::test_fail *FALLADO*",
            "*test_verbose_reporting.py::test_pass *PASADO*",
            "*test_verbose_reporting.py::TestClass::test_skip *OMITIDO*",
            "*test_verbose_reporting.py::test_gen*0* *FALLADO*",
        ])
        assert result.ret == 1

    def test_quiet_reporting(self, testdir):
        p1 = testdir.makepyfile("def test_pass(): pass")
        result = testdir.runpytest('--language=es', p1, '-q')
        s = result.stdout.str()
        assert 'comienza la sesión de prueba' not in s
        assert p1.basename not in s
        assert "===" not in s
        assert "pasado" in s

    def test_more_quiet_reporting(self, testdir):
        p1 = testdir.makepyfile("def test_pass(): pass")
        result = testdir.runpytest('--language=es', p1, '-qq')
        s = result.stdout.str()
        assert 'comienza la sesión de prueba' not in s
        assert p1.basename not in s
        assert "===" not in s
        assert "pasado" not in s

    def test_report_collectionfinish_hook(self, testdir):
        testdir.makeconftest("""
            def pytest_report_collectionfinish(config, startdir, items):
                return ['hello from hook: {0} items'.format(len(items))]
        """)
        testdir.makepyfile("""
            import pytest
            @pytest.mark.parametrize('i', range(3))
            def test(i):
                pass
        """)
        result = testdir.runpytest('--language=es')
        result.stdout.fnmatch_lines([
            "coleccionado 3 ítems",
        ])


@pytest.mark.parametrize('verbose', [True, False])
def test_color_yes_collection_on_non_atty(testdir, verbose):
    """skip collect progress report when working on non-terminals.
    #1397
    """
    testdir.makepyfile("""
        import pytest
        @pytest.mark.parametrize('i', range(10))
        def test_this(i):
            assert 1
    """)
    args = ['--color=yes']
    if verbose:
        args.append('-vv')
    result = testdir.runpytest('--language=es', *args)
    assert 'comienza la sesión de prueba' in result.stdout.str()
    assert '\x1b[1m' in result.stdout.str()
    assert 'coleccionando 10 ítems' not in result.stdout.str()
    if verbose:
        assert 'coleccionando ...' in result.stdout.str()
    assert 'coleccionado 10 ítems' in result.stdout.str()


def test_terminalreporter_reportopt_addopts(testdir):
    testdir.makeini("[pytest]\naddopts=-rs")
    testdir.makepyfile("""
        import pytest

        @pytest.fixture
        def tr(request):
            tr = request.config.pluginmanager.getplugin("terminalreporter")
            return tr
        def test_opt(tr):
            assert tr.hasopt('skipped')
            assert not tr.hasopt('qwe')
    """)
    result = testdir.runpytest('--language=es')
    result.stdout.fnmatch_lines([
        "*1 pasado*"
    ])


def test_terminalreporter_picksup_ini_file(testdir):
    testdir.makeini("[pytest]\naddopts=--language=es")
    testdir.makepyfile("""
        import pytest
        def test_foo():
            pass
    """)
    result = testdir.runpytest()
    result.stdout.fnmatch_lines([
        "*1 pasado*"
    ])


class TestGenericReporting(object):
    """ this test class can be subclassed with a different option
        provider to run e.g. distributed tests.
    """

    def test_collect_fail(self, testdir, option):
        testdir.makepyfile("import xyz\n")
        result = testdir.runpytest('--language=es', *option.args)
        result.stdout.fnmatch_lines([
            "*1 error*",
        ])

    def test_maxfailures(self, testdir, option):
        testdir.makepyfile("""
            def test_1():
                assert 0
            def test_2():
                assert 0
            def test_3():
                assert 0
        """)
        result = testdir.runpytest('--language=es', "--maxfail=2", *option.args)
        result.stdout.fnmatch_lines([
            "*def test_1():*",
            "*def test_2():*",
            "*2 fallado*",
        ])


def test_fdopen_kept_alive_issue124(testdir):
    testdir.makepyfile("""
        import os, sys
        k = []
        def test_open_file_and_keep_alive(capfd):
            stdout = os.fdopen(1, 'w', 1)
            k.append(stdout)

        def test_close_kept_alive_file():
            stdout = k.pop()
            stdout.close()
    """)
    result = testdir.runpytest('--language=es')
    result.stdout.fnmatch_lines([
        "*2 pasado*"
    ])


@pytest.mark.parametrize("exp_color, exp_line, stats_arg", [
    # The method under test only cares about the length of each
    # dict value, not the actual contents, so tuples of anything
    # suffice

    # Important statuses -- the highest priority of these always wins
    ("red", "1 fallado", {"failed": (1,)}),
    ("red", "1 fallado, 1 pasado", {"failed": (1,), "passed": (1,)}),

    ("red", "1 error", {"error": (1,)}),
    ("red", "1 pasado, 1 error", {"error": (1,), "passed": (1,)}),

    # (a status that's not known to the code)
    ("yellow", "1 weird", {"weird": (1,)}),
    ("yellow", "1 pasado, 1 weird", {"weird": (1,), "passed": (1,)}),

    ("yellow", "1 advertencias", {"warnings": (1,)}),
    ("yellow", "1 pasado, 1 advertencias", {"warnings": (1,),
                                            "passed": (1,)}),

    ("green", "5 pasado", {"passed": (1, 2, 3, 4, 5)}),


    # "Boring" statuses.  These have no effect on the color of the summary
    # line.  Thus, if *every* test has a boring status, the summary line stays
    # at its default color, i.e. yellow, to warn the user that the test run
    # produced no useful information
    ("yellow", "1 omitido", {"skipped": (1,)}),
    ("green", "1 pasado, 1 omitido", {"skipped": (1,), "passed": (1,)}),

    ("yellow", "1 deseleccionado", {"deselected": (1,)}),
    ("green", "1 pasado, 1 deseleccionado", {"deselected": (1,), "passed": (1,)}),

    ("yellow", "1 xfailed", {"xfailed": (1,)}),
    ("green", "1 pasado, 1 xfailed", {"xfailed": (1,), "passed": (1,)}),

    ("yellow", "1 xpassed", {"xpassed": (1,)}),
    ("green", "1 pasado, 1 xpassed", {"xpassed": (1,), "passed": (1,)}),

    # Likewise if no tests were found at all
    ("yellow", "No se ejecutó ninguna prueba", {}),

    # Test the empty-key special case
    ("yellow", "No se ejecutó ninguna prueba", {"": (1,)}),
    ("green", "1 pasado", {"": (1,), "passed": (1,)}),


    # A couple more complex combinations
    ("red", "1 fallado, 2 pasado, 3 xfailed",
        {"passed": (1, 2), "failed": (1,), "xfailed": (1, 2, 3)}),

    ("green", "1 pasado, 2 omitido, 3 deseleccionado, 2 xfailed",
        {"passed": (1,),
         "skipped": (1, 2),
         "deselected": (1, 2, 3),
         "xfailed": (1, 2)}),
])
def test_summary_stats(exp_line, exp_color, stats_arg):
    language = Spanish()
    print("Based on stats: %s" % stats_arg)
    print("Expect summary: \"%s\"; with color \"%s\"" % (exp_line, exp_color))
    (line, color) = build_summary_stats_line(stats_arg,
                                             translation_table=language.get_summary_stats_translations(),
                                             no_tests_ran=language.no_tests_ran())
    print("Actually got:   \"%s\"; with color \"%s\"" % (line, color))
    assert line == exp_line
    assert color == exp_color


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
            from _pytest.spanish import Spanish
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
