import os
from uuid import UUID
from allure_commons.utils import md5
from allure_commons.model2 import StatusDetails
from allure_commons.model2 import Status
from allure_commons.model2 import Parameter
from allure_commons.utils import format_exception


ALLURE_LINK_MARK = 'allure_link'


def get_step_name(node, step):
    name = "{step_keyword} {step_name}".format(step_keyword=step.keyword, step_name=step.name)
    if hasattr(node, 'callspec'):
        for key, value in node.callspec.params.items():
            name = name.replace("<{key}>".format(key=key), "<{{{key}}}>".format(key=key))
            name = name.format(**node.callspec.params)
    return name


def get_name(node, scenario):
    if hasattr(node, 'callspec'):
        parts = node.nodeid.rsplit("[")
        return "{name} [{params}".format(name=scenario.name, params=parts[-1])
    return scenario.name


def get_full_name(feature, scenario):
    feature_path = os.path.normpath(feature.rel_filename)
    return "{feature}:{scenario}".format(feature=feature_path, scenario=scenario.name)


def get_uuid(*args):
    return str(UUID(md5(*args)))


def get_status_details(exception):
    message = str(exception)
    trace = format_exception(type(exception), exception)
    return StatusDetails(message=message, trace=trace) if message or trace else None


def get_pytest_report_status(pytest_report):
    pytest_statuses = ('failed', 'passed', 'skipped')
    statuses = (Status.FAILED, Status.PASSED, Status.SKIPPED)
    for pytest_status, status in zip(pytest_statuses, statuses):
        if getattr(pytest_report, pytest_status):
            return status


def get_params(node):
    if hasattr(node, 'callspec'):
        params = node.callspec.params
        return [Parameter(name=name, value=value) for name, value in params.items()]


def allure_links(item):
    for mark in item.iter_markers(name=ALLURE_LINK_MARK):
        yield (mark.kwargs["link_type"], mark.args[0], mark.kwargs["name"])
