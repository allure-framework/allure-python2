import pytest
import allure_commons
from allure_commons.utils import escape_non_unicode_symbols
from allure_commons.utils import now
from allure_commons.utils import uuid4
from allure_commons.utils import represent
from allure_commons.utils import platform_label
from allure_commons.utils import host_tag, thread_tag
from allure_commons.reporter import AllureReporter
from allure_commons.model2 import TestStepResult, TestResult, TestBeforeResult, TestAfterResult
from allure_commons.model2 import TestResultContainer
from allure_commons.model2 import StatusDetails
from allure_commons.model2 import Parameter
from allure_commons.model2 import Label, Link
from allure_commons.model2 import Status
from allure_commons.types import LabelType, AttachmentType
from allure_pytest.utils import allure_description, allure_description_html
from allure_pytest.utils import allure_labels, allure_links, pytest_markers
from allure_pytest.utils import allure_full_name, allure_package, allure_name
from allure_pytest.utils import allure_suite_labels
from allure_pytest.utils import get_status, get_status_details
from allure_pytest.utils import get_outcome_status, get_outcome_status_details
from allure_pytest.utils import get_pytest_report_status
from allure_commons.utils import md5


class AllureListener(object):

    def __init__(self, config):
        self.config = config
        self.allure_logger = AllureReporter()
        self._cache = ItemCache()
        self._host = host_tag()
        self._thread = thread_tag()

    @allure_commons.hookimpl
    def start_step(self, uuid, title, params):
        parameters = [Parameter(name=name, value=value) for name, value in params.items()]
        step = TestStepResult(name=title, start=now(), parameters=parameters)
        self.allure_logger.start_step(None, uuid, step)

    @allure_commons.hookimpl
    def stop_step(self, uuid, exc_type, exc_val, exc_tb):
        self.allure_logger.stop_step(uuid,
                                     stop=now(),
                                     status=get_status(exc_val),
                                     statusDetails=get_status_details(exc_type, exc_val, exc_tb))

    @allure_commons.hookimpl
    def start_fixture(self, parent_uuid, uuid, name):
        after_fixture = TestAfterResult(name=name, start=now())
        self.allure_logger.start_after_fixture(parent_uuid, uuid, after_fixture)

    @allure_commons.hookimpl
    def stop_fixture(self, parent_uuid, uuid, name, exc_type, exc_val, exc_tb):
        self.allure_logger.stop_after_fixture(uuid,
                                              stop=now(),
                                              status=get_status(exc_val),
                                              statusDetails=get_status_details(exc_type, exc_val, exc_tb))

    @pytest.hookimpl(hookwrapper=True, tryfirst=True)
    def pytest_runtest_protocol(self, item, nextitem):
        uuid = self._cache.push(item.nodeid)
        test_result = TestResult(name=item.name, uuid=uuid, start=now(), stop=now())
        self.allure_logger.schedule_test(uuid, test_result)
        yield

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_setup(self, item):
        if not self._cache.get(item.nodeid):
            uuid = self._cache.push(item.nodeid)
            test_result = TestResult(name=item.name, uuid=uuid, start=now(), stop=now())
            self.allure_logger.schedule_test(uuid, test_result)

        yield

        uuid = self._cache.get(item.nodeid)
        test_result = self.allure_logger.get_test(uuid)
        for fixturedef in _test_fixtures(item):
            group_uuid = self._cache.get(fixturedef)
            if not group_uuid:
                group_uuid = self._cache.push(fixturedef)
                group = TestResultContainer(uuid=group_uuid)
                self.allure_logger.start_group(group_uuid, group)
            self.allure_logger.update_group(group_uuid, children=uuid)
        params = item.callspec.params if hasattr(item, 'callspec') else {}

        test_result.name = allure_name(item, params)
        full_name = allure_full_name(item)
        test_result.fullName = full_name
        test_result.historyId = md5(item.nodeid)
        test_result.testCaseId = md5(full_name)
        test_result.description = allure_description(item)
        test_result.descriptionHtml = allure_description_html(item)
        current_param_names = [param.name for param in test_result.parameters]
        test_result.parameters.extend(
            [Parameter(name=name, value=represent(value)) for name, value in params.items()
             if name not in current_param_names])

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_call(self, item):
        uuid = self._cache.get(item.nodeid)
        test_result = self.allure_logger.get_test(uuid)
        if test_result:
            self.allure_logger.drop_test(uuid)
            self.allure_logger.schedule_test(uuid, test_result)
            test_result.start = now()
        yield
        if test_result:
            test_result.stop = now()

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_teardown(self, item):
        yield
        uuid = self._cache.get(item.nodeid)
        test_result = self.allure_logger.get_test(uuid)
        test_result.labels.extend([Label(name=name, value=value) for name, value in allure_labels(item)])
        test_result.labels.extend([Label(name=LabelType.TAG, value=value) for value in pytest_markers(item)])
        test_result.labels.extend([Label(name=name, value=value) for name, value in allure_suite_labels(item)])
        test_result.labels.append(Label(name=LabelType.HOST, value=self._host))
        test_result.labels.append(Label(name=LabelType.THREAD, value=self._thread))
        test_result.labels.append(Label(name=LabelType.FRAMEWORK, value='pytest'))
        test_result.labels.append(Label(name=LabelType.LANGUAGE, value=platform_label()))
        test_result.labels.append(Label(name='package', value=allure_package(item)))
        test_result.links.extend([Link(link_type, url, name) for link_type, url, name in allure_links(item)])

    @pytest.hookimpl(hookwrapper=True)
    def pytest_fixture_setup(self, fixturedef, request):
        fixture_name = getattr(fixturedef.func, '__allure_display_name__', fixturedef.argname)

        container_uuid = self._cache.get(fixturedef)

        if not container_uuid:
            container_uuid = self._cache.push(fixturedef)
            container = TestResultContainer(uuid=container_uuid)
            self.allure_logger.start_group(container_uuid, container)

        self.allure_logger.update_group(container_uuid, start=now())

        before_fixture_uuid = uuid4()
        before_fixture = TestBeforeResult(name=fixture_name, start=now())
        self.allure_logger.start_before_fixture(container_uuid, before_fixture_uuid, before_fixture)

        outcome = yield

        self.allure_logger.stop_before_fixture(before_fixture_uuid,
                                               stop=now(),
                                               status=get_outcome_status(outcome),
                                               statusDetails=get_outcome_status_details(outcome))

        finalizers = getattr(fixturedef, '_finalizers', [])
        for index, finalizer in enumerate(finalizers):
            name = '{fixture}::{finalizer}'.format(fixture=fixture_name,
                                                   finalizer=getattr(finalizer, "__name__", index))
            finalizers[index] = allure_commons.fixture(finalizer, parent_uuid=container_uuid, name=name)

    @pytest.hookimpl(hookwrapper=True)
    def pytest_fixture_post_finalizer(self, fixturedef):
        yield
        if hasattr(fixturedef, 'cached_result') and self._cache.get(fixturedef):
            container_uuid = self._cache.pop(fixturedef)
            self.allure_logger.stop_group(container_uuid, stop=now())

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        uuid = self._cache.get(item.nodeid)

        report = (yield).get_result()

        test_result = self.allure_logger.get_test(uuid)
        status = get_pytest_report_status(report)
        status_details = None

        if call.excinfo:
            message = escape_non_unicode_symbols(call.excinfo.exconly())
            if hasattr(report, 'wasxfail'):
                reason = report.wasxfail
                message = ('XFAIL {}'.format(reason) if reason else 'XFAIL') + '\n\n' + message
            trace = escape_non_unicode_symbols(report.longreprtext)
            status_details = StatusDetails(
                message=message,
                trace=trace)
            if (status != Status.SKIPPED
                    and not (call.excinfo.errisinstance(AssertionError)
                             or call.excinfo.errisinstance(pytest.fail.Exception))):
                status = Status.BROKEN

        if status == Status.PASSED and hasattr(report, 'wasxfail'):
            reason = report.wasxfail
            message = 'XPASS {reason}'.format(reason=reason) if reason else 'XPASS'
            status_details = StatusDetails(message=message)

        if report.when == 'setup':
            test_result.status = status
            test_result.statusDetails = status_details

        if report.when == 'call':
            if test_result.status == Status.PASSED:
                test_result.status = status
                test_result.statusDetails = status_details

        if report.when == 'teardown':
            if status in (Status.FAILED, Status.BROKEN) and test_result.status == Status.PASSED:
                test_result.status = status
                test_result.statusDetails = status_details

            if self.config.option.attach_capture:
                if report.caplog:
                    self.attach_data(report.caplog, "log", AttachmentType.TEXT, None)
                if report.capstdout:
                    self.attach_data(report.capstdout, "stdout", AttachmentType.TEXT, None)
                if report.capstderr:
                    self.attach_data(report.capstderr, "stderr", AttachmentType.TEXT, None)

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_logfinish(self, nodeid, location):
        yield
        uuid = self._cache.pop(nodeid)
        if uuid:
            self.allure_logger.close_test(uuid)

    @allure_commons.hookimpl
    def attach_data(self, body, name, attachment_type, extension):
        self.allure_logger.attach_data(uuid4(), body, name=name, attachment_type=attachment_type, extension=extension)

    @allure_commons.hookimpl
    def attach_file(self, source, name, attachment_type, extension):
        self.allure_logger.attach_file(uuid4(), source, name=name, attachment_type=attachment_type, extension=extension)

    @allure_commons.hookimpl
    def add_title(self, test_title):
        test_result = self.allure_logger.get_test(None)
        if test_result:
            test_result.name = test_title

    @allure_commons.hookimpl
    def add_description(self, test_description):
        test_result = self.allure_logger.get_test(None)
        if test_result:
            test_result.description = test_description

    @allure_commons.hookimpl
    def add_description_html(self, test_description_html):
        test_result = self.allure_logger.get_test(None)
        if test_result:
            test_result.descriptionHtml = test_description_html

    @allure_commons.hookimpl
    def add_link(self, url, link_type, name):
        test_result = self.allure_logger.get_test(None)
        if test_result:
            pattern = dict(self.config.option.allure_link_pattern).get(link_type, u'{}')
            link_url = pattern.format(url)
            new_link = Link(link_type, link_url, link_url if name is None else name)
            for link in test_result.links:
                if link.url == new_link.url:
                    return
            test_result.links.append(new_link)

    @allure_commons.hookimpl
    def add_label(self, label_type, labels):
        test_result = self.allure_logger.get_test(None)
        for label in labels if test_result else ():
            test_result.labels.append(Label(label_type, label))

    @allure_commons.hookimpl
    def add_parameter(self, name, value):
        test_result: TestResult = self.allure_logger.get_test(None)
        existed_parameter = list(filter(lambda x: x.name == name, test_result.parameters))
        if existed_parameter:
            existed_parameter[0].value = represent(value)
        else:
            test_result.parameters.append(Parameter(name=name, value=represent(value)))


class ItemCache(object):

    def __init__(self):
        self._items = dict()

    def get(self, _id):
        return self._items.get(str(_id))

    def push(self, _id):
        return self._items.setdefault(str(_id), uuid4())

    def pop(self, _id):
        return self._items.pop(str(_id), None)


def _test_fixtures(item):
    fixturemanager = item.session._fixturemanager
    fixturedefs = []

    if hasattr(item, "_request") and hasattr(item._request, "fixturenames"):
        for name in item._request.fixturenames:
            fixturedef = fixturemanager.getfixturedefs(name, item.nodeid)
            if fixturedef:
                fixturedefs.append(fixturedef[-1])

    return fixturedefs
