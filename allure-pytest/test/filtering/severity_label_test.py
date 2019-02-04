"""
>>> allure_report = getfixture('allure_report_with_params')('--allure-severities=trivial')
>>> assert_that(allure_report,
...             all_of(
...                 has_property('test_cases', has_length(5)),
...                 has_property('test_groups', has_length(0))
...             ))  # doctest: +SKIP
"""

import allure


@allure.severity(allure.severity_level.TRIVIAL)
def test_function_with_trivial_severity():
    """
    >>> allure_report = getfixture('allure_report_with_params')('--allure-severities=trivial')
    >>> assert_that(allure_report,
    ...             has_test_case('test_function_with_trivial_severity',
    ...                           with_status('passed')
    ...             )
    ... )
    """
    pass


def test_function_with_default_severity():
    """
    >>> allure_report = getfixture('allure_report_with_params')('--allure-severities=normal')
    >>> assert_that(allure_report,
    ...             has_test_case('test_function_with_default_severity',
    ...                           with_status('passed')
    ...             )
    ... )
    """
    pass


class TestClass(object):

    @allure.severity(allure.severity_level.TRIVIAL)
    def test_method_with_trivial_severity(self):
        """
        >>> allure_report = getfixture('allure_report_with_params')('--allure-severities=trivial')
        >>> assert_that(allure_report,
        ...             has_test_case('test_method_with_trivial_severity',
        ...                           with_status('passed')
        ...             )
        ... )
        """
        pass

    @allure.severity(allure.severity_level.NORMAL)
    def test_method_with_normal_severity(self):
        """
        >>> from hamcrest import not_
        >>> allure_report = getfixture('allure_report_with_params')('--allure-severities=trivial')
        >>> assert_that(allure_report,
        ...             not_(has_test_case('test_method_with_normal_severity'))
        ... )
        """
        pass


@allure.severity(allure.severity_level.TRIVIAL)
class TestClassAgain(object):

    def test_method_with_whole_class_trivial_severity(self):
        """
        >>> allure_report = getfixture('allure_report_with_params')('--allure-severities=trivial')
        >>> assert_that(allure_report,
        ...             has_test_case('test_method_with_whole_class_trivial_severity',
        ...                           with_status('passed')
        ...             )
        ... )
        """
        pass

    @allure.severity(allure.severity_level.NORMAL)
    def test_method_with_overridden_class_severity(self):
        """
        >>> from hamcrest import not_
        >>> allure_report = getfixture('allure_report_with_params')('--allure-severities=trivial')
        >>> assert_that(allure_report,
        ...             not_(has_test_case('test_method_with_overridden_class_severity'))
        ... )
        """
        pass
