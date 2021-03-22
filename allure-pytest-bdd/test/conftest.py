import pytest
import mock
from contextlib import contextmanager
import allure_commons
from allure_commons_test.report import AllureReport
from allure_commons.logger import AllureFileLogger
from .steps import *  # noqa F401 F403
from pytest_bdd import given, when, parsers

from .py_file_builder import PyFileBuilder

pytest_plugins = "pytester"


@contextmanager
def fake_logger(path, logger):
    blocked_plugins = []
    for name, plugin in allure_commons.plugin_manager.list_name_plugin():
        allure_commons.plugin_manager.unregister(plugin=plugin, name=name)
        blocked_plugins.append(plugin)

    with mock.patch(path) as ReporterMock:
        ReporterMock.return_value = logger
        yield

    for plugin in blocked_plugins:
        allure_commons.plugin_manager.register(plugin)


class AlluredTestdir(object):
    def __init__(self, testdir, request):
        self.testdir = testdir
        self.request = request
        self.allure_report = None

    def run_with_allure(self):
        logger = AllureFileLogger(self.testdir.tmpdir.strpath)
        with fake_logger("allure_pytest_bdd.plugin.AllureFileLogger", logger):
            self.testdir.runpytest("-s", "-v", "--alluredir", self.testdir.tmpdir)
            # print(a.stdout.lines)
            # print(a.stderr.lines)
            self.allure_report = AllureReport(self.testdir.tmpdir.strpath)


@pytest.fixture
def allured_testdir(testdir, request):
    return AlluredTestdir(testdir, request)


@pytest.fixture
def context():
    return dict()


@pytest.fixture
def allure_report(allured_testdir, context):
    return allured_testdir.allure_report


@given(parsers.re("(?P<name>\\w+)(?P<extension>\\.\\w+) with content:(?:\n)(?P<content>[\\S|\\s]*)"))
def feature_definition(name, extension, content, testdir):
    testdir.makefile(extension, **dict([(name, content)]))


@when("run pytest-bdd with allure")
def run(allured_testdir):
    allured_testdir.run_with_allure()


@pytest.fixture()
@given(parsers.parse("py file with name: {name}"))
def current_py_file_builder(name):
    return PyFileBuilder(name)


@given(parsers.parse("with imports: {modules}"))
def add_imports_in_builder(modules, current_py_file_builder):
    modules_names = [module.strip() for module in modules.split(",")]
    current_py_file_builder.add_imports(*modules_names)


@given(parsers.re("with func:(?:\n)(?P<content>[\\S|\\s]*)"))
def add_func_in_builder(content, current_py_file_builder):
    current_py_file_builder.add_func(content)


@given("with passed steps")
def add_passed_steps(current_py_file_builder):

    passed_steps = '@pytest_bdd.given("passed step")\n' \
                   '@pytest_bdd.when("passed step")\n' \
                   '@pytest_bdd.then("passed step")\n' \
                   'def step_impl():\n' \
                   '    pass'

    current_py_file_builder.add_func(passed_steps)


@given(parsers.parse("test for {scenario_name} from {feature_file}"))
def add_scenario_step(scenario_name, feature_file, current_py_file_builder):

    scenario_func = f'@pytest_bdd.scenario("{feature_file}", "{scenario_name}")\n' \
                     'def test_scenario():\n' \
                     '    pass'

    current_py_file_builder.add_func(scenario_func)


@given(parsers.parse("py file saved"))
def save_py_file(current_py_file_builder, testdir):
    testdir.makefile(
        ".py",
        **dict([(current_py_file_builder.name, current_py_file_builder.get_content())]))
