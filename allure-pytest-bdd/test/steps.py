from pytest_bdd import then
from pytest_bdd import parsers
from functools import partial
from hamcrest import assert_that
# from hamcrest import not_
from allure_commons_test.report import has_test_case
from allure_commons_test.result import with_status
from allure_commons_test.result import has_step
# from allure_commons_test.result import has_attachment
from allure_commons_test.result import has_parameter
from allure_commons_test.result import has_history_id
# from allure_commons_test.result import has_status_details
# from allure_commons_test.result import with_message_contains
# from allure_commons_test.result import has_link
# from allure_commons_test.container import has_container
# from allure_commons_test.container import has_before, has_after
# from allure_commons_test.label import has_severity
# from allure_commons_test.label import has_tag
# from allure_commons_test.label import has_label


def match(matcher, *args):
    for i, arg in enumerate(args):
        if not hasattr(arg, '__call__'):
            matcher = partial(matcher, arg)
        else:
            matcher = partial(matcher, match(arg, *args[i+1:]))
            break
    return matcher()


@then(parsers.re("allure report has result for (?:\")(?P<scenario_name>[\\w|\\s|,]*)(?:\") scenario"))
def match_scenario(allure_report, context, scenario_name):
    matcher = partial(match, has_test_case, scenario_name)
    assert_that(allure_report, matcher())
    context['scenario'] = matcher


@then(parsers.parse("this {item:w} has {status:w} status"))
def item_status(allure_report, context, item, status):
    context_matcher = context[item]
    matcher = partial(context_matcher, with_status, status)
    assert_that(allure_report, matcher())


@then(parsers.parse("this {item:w} has a history id"))
def item_history_id(allure_report, context, item):
    context_matcher = context[item]
    matcher = partial(context_matcher, has_history_id)
    assert_that(allure_report, matcher())


@then(parsers.re("this (?P<item>\\w+) "
                 "has parameter (?:\")(?P<param_name>[\\w|\\s]*)(?:\") "
                 "with value (?:\")(?P<param_value>[\\w|\\s]*)(?:\")"))
def item_parameter(allure_report, context, item, param_name, param_value):
    context_matcher = context[item]
    matcher = partial(context_matcher, has_parameter, param_name, param_value)
    assert_that(allure_report, matcher())


@then(parsers.re("this (?P<item>\\w+) contains (?:\")(?P<step>[\\w|\\s|>|<]+)(?:\") step"))
def step_step(allure_report, context, item, step):
    context_matcher = context[item]
    matcher = partial(context_matcher, has_step, step)
    context["step"] = matcher
    assert_that(allure_report, matcher())
