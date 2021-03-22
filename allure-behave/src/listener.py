# -*- coding: utf-8 -*-

from collections import deque
import allure_commons
from allure_commons.reporter import AllureReporter
from allure_commons.utils import uuid4
from allure_commons.utils import now
from allure_commons.utils import platform_label
from allure_commons.types import LabelType, AttachmentType, LinkType
from allure_commons.model2 import TestResult
from allure_commons.model2 import TestStepResult
from allure_commons.model2 import TestBeforeResult, TestAfterResult
from allure_commons.model2 import TestResultContainer
from allure_commons.model2 import Parameter, Label, Link
from allure_behave.utils import scenario_parameters
from allure_behave.utils import scenario_name
from allure_behave.utils import scenario_history_id
from allure_behave.utils import step_status, step_status_details
from allure_behave.utils import scenario_status, scenario_status_details
from allure_behave.utils import step_table
from allure_behave.utils import get_status, get_status_details
from allure_behave.utils import scenario_links
from allure_behave.utils import scenario_labels
from allure_behave.utils import get_fullname
from allure_behave.utils import TEST_PLAN_SKIP_REASON


BEFORE_FIXTURES = ['before_all', 'before_tag', 'before_feature', 'before_scenario']
AFTER_FIXTURES = ['after_all', 'after_tag', 'after_feature', 'after_scenario']
FIXTURES = BEFORE_FIXTURES + AFTER_FIXTURES


class AllureListener(object):
    def __init__(self, behave_config):
        self.behave_config = behave_config
        self.issue_pattern = behave_config.userdata.get('AllureFormatter.issue_pattern', None)
        self.link_pattern = behave_config.userdata.get('AllureFormatter.link_pattern', None)
        self.logger = AllureReporter()
        self.current_step_uuid = None
        self.current_scenario_uuid = None
        self.execution_context = Context()
        self.fixture_context = Context()
        self.steps = deque()

    def __del__(self):
        for group in self.fixture_context.exit():
            group.children.extend(self.execution_context)
            self.logger.stop_group(group.uuid)

    @allure_commons.hookimpl
    def start_fixture(self, parent_uuid, uuid, name, parameters):
        parameters = [Parameter(name=param_name, value=param_value) for param_name, param_value in parameters.items()]

        if name in FIXTURES and not self.fixture_context:
            group = TestResultContainer(uuid=uuid4())
            self.logger.start_group(group.uuid, group)
            self.fixture_context.append(group)

        if name in BEFORE_FIXTURES:
            fixture = TestBeforeResult(name=name, start=now(), parameters=parameters)
            for group in self.fixture_context:
                self.logger.start_before_fixture(group.uuid, uuid, fixture)

        elif name in AFTER_FIXTURES:
            fixture = TestAfterResult(name=name, start=now(), parameters=parameters)
            for group in self.fixture_context:
                self.logger.start_after_fixture(group.uuid, uuid, fixture)

    @allure_commons.hookimpl
    def stop_fixture(self, parent_uuid, uuid, name, exc_type, exc_val, exc_tb):
        if name in FIXTURES:
            self.logger.stop_before_fixture(uuid=uuid,
                                            stop=now(),
                                            status=get_status(exc_val),
                                            statusDetails=get_status_details(exc_type, exc_val, exc_tb))

    def start_feature(self):
        self.execution_context.enter()
        self.fixture_context.enter()

    def stop_feature(self):
        uuids = self.execution_context.exit()
        for group in self.fixture_context.exit():
            group.children.extend(uuids)
            self.logger.stop_group(group.uuid)
        self.execution_context.extend(uuids)

    @allure_commons.hookimpl
    def start_test(self, parent_uuid, uuid, name, parameters, context):
        self.start_scenario(context['scenario'])

    def start_scenario(self, scenario):
        self.current_scenario_uuid = uuid4()
        self.fixture_context.enter()
        self.execution_context.enter()
        self.execution_context.append(self.current_scenario_uuid)

        test_case = TestResult(uuid=self.current_scenario_uuid, start=now())
        test_case.name = scenario_name(scenario)
        test_case.fullName = get_fullname(scenario)
        test_case.historyId = scenario_history_id(scenario)
        test_case.description = '\n'.join(scenario.description)
        test_case.parameters = scenario_parameters(scenario)

        test_case.links.extend(scenario_links(
            scenario,
            issue_pattern=self.issue_pattern,
            link_pattern=self.link_pattern))
        test_case.labels.extend(scenario_labels(scenario))
        test_case.labels.append(Label(name=LabelType.FEATURE, value=scenario.feature.name))
        test_case.labels.append(Label(name=LabelType.FRAMEWORK, value='behave'))
        test_case.labels.append(Label(name=LabelType.LANGUAGE, value=platform_label()))
        test_case.labels.append(Label(name=LabelType.SUITE, value=scenario.feature.name))
        test_case.labels.append(Label(name=LabelType.PACKAGE, value=scenario.feature.name))

        self.logger.schedule_test(self.current_scenario_uuid, test_case)

    @allure_commons.hookimpl
    def stop_test(self, parent_uuid, uuid, name, context, exc_type, exc_val, exc_tb):
        self.stop_scenario(context['scenario'])

    def stop_scenario(self, scenario):
        if scenario.status == 'skipped' \
                and not self.behave_config.show_skipped or scenario.skip_reason == TEST_PLAN_SKIP_REASON:
            self.logger.drop_test(self.current_scenario_uuid)
        else:
            status = scenario_status(scenario)
            status_details = scenario_status_details(scenario)

            self.flush_steps()
            test_result = self.logger.get_test(self.current_scenario_uuid)
            test_result.stop = now()
            test_result.status = status
            test_result.statusDetails = status_details
            self.logger.close_test(self.current_scenario_uuid)
            self.current_step_uuid = None

            for group in self.fixture_context.exit():
                group.children.append(self.current_scenario_uuid)
                self.logger.stop_group(group.uuid)

        self.execution_context.exit()
        self.execution_context.append(self.current_scenario_uuid)
        self.current_scenario_uuid = None

    def schedule_step(self, step):
        self.steps.append(step)

    def match_step(self, match):
        step = self.steps.popleft()
        self.start_behave_step(step)

    def start_behave_step(self, step):

        self.current_step_uuid = uuid4()
        name = u'{keyword} {title}'.format(keyword=step.keyword, title=step.name)

        allure_step = TestStepResult(name=name, start=now())
        self.logger.start_step(None, self.current_step_uuid, allure_step)

        if step.text:
            self.logger.attach_data(uuid4(), step.text, name='.text', attachment_type=AttachmentType.TEXT)

        if step.table:
            self.logger.attach_data(uuid4(), step_table(step), name='.table', attachment_type=AttachmentType.CSV)

    def stop_behave_step(self, result):
        status = step_status(result)
        status_details = step_status_details(result)
        self.logger.stop_step(self.current_step_uuid, stop=now(), status=status, statusDetails=status_details)

    def flush_steps(self):
        while self.steps:
            step = self.steps.popleft()
            self.start_behave_step(step)
            self.stop_behave_step(step)

    @allure_commons.hookimpl
    def start_step(self, uuid, title, params):
        parameters = [Parameter(name=name, value=value) for name, value in params.items()]
        step = TestStepResult(name=title, start=now(), parameters=parameters)
        self.logger.start_step(None, uuid, step)

    @allure_commons.hookimpl
    def stop_step(self, uuid, exc_type, exc_val, exc_tb):
        self.logger.stop_step(uuid,
                              stop=now(),
                              status=get_status(exc_val),
                              statusDetails=get_status_details(exc_type, exc_val, exc_tb))

    @allure_commons.hookimpl
    def attach_data(self, body, name, attachment_type, extension):
        self.logger.attach_data(uuid4(), body, name=name, attachment_type=attachment_type, extension=extension)

    @allure_commons.hookimpl
    def attach_file(self, source, name, attachment_type, extension):
        self.logger.attach_file(uuid4(), source, name=name, attachment_type=attachment_type, extension=extension)

    @allure_commons.hookimpl
    def add_description(self, test_description):
        test_result = self.logger.get_test(None)
        if test_result:
            test_result.description = test_description

    @allure_commons.hookimpl
    def add_description_html(self, test_description_html):
        test_result = self.logger.get_test(None)
        if test_result:
            test_result.descriptionHtml = test_description_html

    @allure_commons.hookimpl
    def add_link(self, url, link_type, name):
        test_result = self.logger.get_test(None)
        if test_result:
            pattern = u'{}'
            if link_type == LinkType.ISSUE and self.issue_pattern:
                pattern = self.issue_pattern
            elif link_type == LinkType.LINK and self.link_pattern:
                pattern = self.link_pattern

            link_url = pattern.format(url)
            new_link = Link(link_type, link_url, link_url if name is None else name)
            for link in test_result.links:
                if link.url == new_link.url:
                    return

            test_result.links.append(new_link)


class Context(list):
    def __init__(self, _list=list()):
        super(Context, self).__init__(_list)
        self._stack = [_list]

    def enter(self, _list=list()):
        self._stack.append(self[:])
        self[:] = _list
        return self

    def exit(self):
        gone, self[:] = self[:], self._stack.pop()
        return gone
