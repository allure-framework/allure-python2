import os
from uuid import UUID
from allure_commons.model2 import StatusDetails
from allure_commons.model2 import Status
from allure_commons.model2 import Parameter
from allure_commons.utils import md5
from allure_commons.utils import format_exception
from allure_commons.utils import represent


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


def pytest_markers(item):
    for keyword in item.keywords.keys():
        if any([
            keyword.startswith('allure_'),
            keyword == 'parametrize',
            keyword == "usefixtures"
        ]):
            continue
        marker = item.get_closest_marker(keyword)
        if marker is None:
            continue

        yield mark_to_str(marker)


def mark_to_str(marker):
    args = [represent(arg) for arg in marker.args]
    kwargs = ['{name}={value}'.format(name=key, value=represent(marker.kwargs[key])) for key in marker.kwargs]
    if marker.name in ('filterwarnings', 'skip', 'skipif', 'xfail', 'tryfirst', 'trylast'):
        markstr = '@pytest.mark.{name}'.format(name=marker.name)
    else:
        markstr = '{name}'.format(name=marker.name)
    if args or kwargs:
        parameters = ', '.join(args + kwargs)
        markstr = '{}({})'.format(markstr, parameters)
    return markstr
