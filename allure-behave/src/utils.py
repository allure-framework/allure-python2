# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from enum import Enum
from behave.runner_util import make_undefined_step_snippet
from allure_commons.types import Severity, LabelType
from allure_commons.model2 import Status, Parameter
from allure_commons.model2 import Link, Label
from allure_commons.model2 import StatusDetails
from allure_commons.utils import md5
from allure_commons.utils import format_exception, format_traceback
from allure_commons.mapping import parse_tag, labels_set

TEST_PLAN_SKIP_REASON = "Not in allure test plan"

STATUS = {
    'passed': Status.PASSED,
    'failed': Status.FAILED,
    'skipped': Status.SKIPPED,
    'untested': Status.SKIPPED,
    'undefined': Status.BROKEN
}


def scenario_name(scenario):
    return scenario.name if scenario.name else scenario.keyword


def scenario_history_id(scenario):
    parts = [scenario.feature.name, scenario.name]
    if scenario._row:
        row = scenario._row
        parts.extend(['{name}={value}'.format(name=name, value=value) for name, value in zip(row.headings, row.cells)])
    return md5(*parts)


def scenario_parameters(scenario):
    row = scenario._row
    return [Parameter(name=name, value=value) for name, value in zip(row.headings, row.cells)] if row else None


def scenario_links(scenario, issue_pattern, link_pattern):
    tags = scenario.feature.tags + scenario.tags
    parsed = [
        parse_tag(item, issue_pattern=issue_pattern, link_pattern=link_pattern)
        for item in tags
    ]
    return filter(lambda x: isinstance(x, Link), parsed)


def scenario_labels(scenario):
    tags = scenario.feature.tags + scenario.tags
    default_labels = [Label(name=LabelType.SEVERITY, value=Severity.NORMAL)]
    parsed = [parse_tag(item) for item in tags]
    return labels_set(list(filter(lambda x: isinstance(x, Label), default_labels + parsed)))


def scenario_status(scenario):
    for step in scenario.all_steps:
        if step_status(step) != 'passed':
            return step_status(step)
    return Status.PASSED


def scenario_status_details(scenario):
    for step in scenario.all_steps:
        if step_status(step) != 'passed':
            return step_status_details(step)


def get_status_details(exc_type, exception, exc_traceback):
    if exception:
        return StatusDetails(message=format_exception(exc_type, exception),
                             trace=format_traceback(exc_traceback))


def step_status(result):
    if isinstance(result.status, Enum):
        status = STATUS.get(result.status.name, None)
    else:
        status = STATUS.get(result.status, None)
    if status != Status.SKIPPED and result.exception:
        status = get_status(result.exception)
    return status


def get_status(exception):
    if exception and isinstance(exception, AssertionError):
        return Status.FAILED
    elif exception:
        return Status.BROKEN
    return Status.PASSED


def get_fullname(scenario):
    name_with_param = scenario_name(scenario)
    name = name_with_param.rsplit(" -- ")[0]
    return "{filename}: {name}".format(filename=scenario.feature.name, name=name)


def step_status_details(result):
    if result.exception:
        # workaround for https://github.com/behave/behave/pull/616
        trace = "\n".join(result.exc_traceback) if type(result.exc_traceback) == list else format_traceback(
            result.exc_traceback)
        return StatusDetails(message=format_exception(type(result.exception), result.exception), trace=trace)

    elif result.status == 'undefined':
        message = '\nYou can implement step definitions for undefined steps with these snippets:\n\n'
        message += make_undefined_step_snippet(result)
        return StatusDetails(message=message)


def step_table(step):
    table = [','.join(step.table.headings)]
    [table.append(','.join(list(row))) for row in step.table.rows]
    return '\n'.join(table)


def is_planned_scenario(scenario, test_plan):
    if test_plan:
        fullname = get_fullname(scenario)
        labels = scenario_labels(scenario)
        id_labels = list(filter(lambda label: label.name == LabelType.ID, labels))
        allure_id = id_labels[0].value if id_labels else None
        for item in test_plan:
            if (allure_id and allure_id == item.get("id")) or fullname == item.get("selector"):
                return
        scenario.skip(reason=TEST_PLAN_SKIP_REASON)
