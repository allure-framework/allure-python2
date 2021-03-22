from __future__ import print_function
import pytest
import os
import sys
import subprocess
import shlex
import hashlib
from inspect import getmembers, isfunction
from allure_commons_test.report import AllureReport
from allure_commons.utils import thread_tag


with open("debug-runner", "w") as debugfile:
    # overwrite debug-runner file with an empty one
    print("New session", file=debugfile)


def _get_hash(input):
    if sys.version_info < (3, 0):
        data = bytes(input)
    else:
        data = bytes(input, 'utf8')
    return hashlib.md5(data).hexdigest()


@pytest.fixture(scope='function', autouse=True)
def inject_matchers(doctest_namespace):
    import hamcrest
    for name, function in getmembers(hamcrest, isfunction):
            doctest_namespace[name] = function

    from allure_commons_test import container, label, report, result
    for module in [container, label, report, result]:
        for name, function in getmembers(module, isfunction):
            doctest_namespace[name] = function


def _runner(allure_dir, module, *extra_params):
    extra_params = ' '.join(extra_params)
    cmd = shlex.split('%s -m pytest --allure-capture --alluredir=%s %s %s' % (sys.executable, allure_dir, extra_params, module),
                      posix=False if os.name == "nt" else True)
    with open("debug-runner", "a") as debugfile:
        try:
            subprocess.check_output(cmd, stderr = subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            # Save to debug file errors on execution (includes pytest failing tests)
            print(e.output, file=debugfile)


@pytest.fixture(scope='module')
def allure_report_with_params(request, tmpdir_factory):
    module = request.module.__file__
    tmpdir = tmpdir_factory.mktemp('data')

    def run_with_params(*params, **kwargs):
        cache = kwargs.get("cache", True)
        key = _get_hash('{thread}{module}{param}'.format(thread=thread_tag(), module=module, param=''.join(params)))
        if not request.config.cache.get(key, False):
            _runner(tmpdir.strpath, module, *params)
            if cache:
                request.config.cache.set(key, True)

                def clear_cache():
                    request.config.cache.set(key, False)
                request.addfinalizer(clear_cache)

        return AllureReport(tmpdir.strpath)
    return run_with_params


@pytest.fixture(scope='module')
def allure_report(request, tmpdir_factory):
    module = request.module.__file__
    tmpdir = tmpdir_factory.mktemp('data')
    _runner(tmpdir.strpath, module)
    return AllureReport(tmpdir.strpath)


def pytest_collection_modifyitems(items, config):
    if config.option.doctestmodules:
        items[:] = [item for item in items if item.__class__.__name__ == 'DoctestItem']


def pytest_ignore_collect(path, config):
    if sys.version_info.major < 3 and "py3_only" in path.strpath:
        return True

    if sys.version_info.major > 2 and "py2_only" in path.strpath:
        return True
