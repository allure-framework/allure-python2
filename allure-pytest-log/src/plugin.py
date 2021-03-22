import allure_commons
from allure_commons.logger import AllureFileLogger
from allure_pytest.listener import AllureListener
from .listener import AllureLogListener


def _enable_allure_capture(config):
    allure_listener = config.pluginmanager.getplugin('AllureListener')

    if not allure_listener:
        # registry allure-pytest(dependency) plugin first
        report_dir = config.option.allure_report_dir or 'reports'
        clean = config.option.clean_alluredir

        allure_listener = AllureListener(config)
        config.pluginmanager.register(allure_listener)
        allure_commons.plugin_manager.register(allure_listener)
        config.add_cleanup(cleanup_factory(allure_listener))

        file_logger = AllureFileLogger(report_dir, clean)
        allure_commons.plugin_manager.register(file_logger)
        config.add_cleanup(cleanup_factory(file_logger))

    allure_log_listener = AllureLogListener(allure_listener)
    config.pluginmanager.register(allure_log_listener)
    allure_commons.plugin_manager.register(allure_log_listener)
    config.add_cleanup(cleanup_factory(allure_log_listener))


def pytest_addoption(parser):
    parser.getgroup("reporting").addoption('--allure-capture',
                                           action="store_true",
                                           dest="allure_capture",
                                           help="Capture standard output to Allure report")


def cleanup_factory(plugin):
    def clean_up():
        name = allure_commons.plugin_manager.get_name(plugin)
        allure_commons.plugin_manager.unregister(name=name)

    return clean_up


def pytest_configure(config):
    allure_capture = config.option.allure_capture
    if allure_capture:
        _enable_allure_capture(config)
