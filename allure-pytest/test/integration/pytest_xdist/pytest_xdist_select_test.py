import allure
import pytest
from hamcrest import assert_that, ends_with, has_entry
from allure_commons_test.report import has_only_testcases


@allure.issue("292")
@allure.feature("Integration")
@pytest.mark.real_logger
def test_xdist_and_select_test_by_bdd_label(allured_testdir):
    """
    >>> import pytest
    >>> import allure

    >>> @pytest.mark.foo
    ... def test_with_mark_foo():
    ...     print ("hello")

    >>> @allure.feature("boo")
    ... def test_with_feature_boo():
    ...     print ("hello")
    """

    allured_testdir.parse_docstring_source()
    allured_testdir.run_with_allure("-v", "--allure-features=boo", "-n1")

    assert_that(allured_testdir.allure_report,
                has_only_testcases(
                    has_entry("fullName",
                              ends_with("test_with_feature_boo")
                              )
                ))


@allure.feature("Integration")
@pytest.mark.real_logger
def test_select_exclusive_test_by_bdd_labels(allured_testdir):
    """
    >>> import pytest
    >>> import allure

    >>> @allure.feature("boo")
    ... def test_with_feature_boo():
    ...     print ("hello")

    >>> @allure.feature("boo", "foo")
    ... def test_with_feature_boo_and_foo():
    ...     print ("hello")
    """

    allured_testdir.parse_docstring_source()
    allured_testdir.run_with_allure("-v", "--allure-features=boo,foo", "--allure-labels-exclusive", "-n1")

    assert_that(allured_testdir.allure_report,
                has_only_testcases(
                    has_entry("fullName",
                              ends_with("test_with_feature_boo_and_foo")
                              )
                ))
