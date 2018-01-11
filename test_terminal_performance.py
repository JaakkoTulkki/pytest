from subprocess import call


def run_tests():
    cmd = 'python pytest.py testing/test_terminal.py '
    call(cmd, shell=True)


def test_all_tests(benchmark):
    benchmark(run_tests)
