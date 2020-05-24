# -*- coding: utf-8 -*-

from allure_commons.utils import represent
from hamcrest import assert_that
from allure_commons_test.report import has_test_case
from allure_commons_test.label import has_tag


def test_pytest_marker(executed_docstring_source):
    """
    >>> import pytest

    >>> @pytest.mark.cool
    ... @pytest.mark.stuff
    ... def test_pytest_marker_example():
    ...     pass
    """

    assert_that(executed_docstring_source.allure_report,
                has_test_case("test_pytest_marker_example",
                              has_tag("cool"),
                              has_tag("stuff")
                              )
                )


def test_pytest_markers(executed_docstring_source):
    """
    >>> import pytest

    >>> @pytest.mark.usermark1
    ... @pytest.mark.usermark2
    ... @pytest.mark.parametrize("param", ["foo"])
    ... @pytest.mark.skipif(False, reason="reason2")
    ... @pytest.mark.skipif(False, reason="reason1")
    ... def test_pytest_markers_example(param):
    ...     pass
    """

    assert_that(executed_docstring_source.allure_report,
                has_test_case('test_omit_pytest_markers_example[foo]',
                              has_tag("usermark1"),
                              has_tag("usermark2"),
                              has_tag("skipif(False, reason='reason2')"),
                              has_tag("skipif(False, reason='reason1')"),
                              has_tag("parametrize('param', ['foo'])")
                              )
                )


def test_pytest_mark_marker_with_args(executed_docstring_source):
    """
    >>> import pytest

    >>> @pytest.mark.marker('cool', 'stuff')
    ... def test_pytest_mark_marker_with_args_example():
    ...     pass
    """

    assert_that(executed_docstring_source.allure_report,
                has_test_case("test_pytest_marker_with_args_example",
                              has_tag("marker('cool', 'stuff')")
                              )
                )


def test_pytest_marker_with_kwargs(executed_docstring_source):
    """
    >>> import pytest

    >>> @pytest.mark.marker(stuff='cool')
    ... def test_pytest_marker_with_kwargs_example():
    ...     pass
    """

    assert_that(executed_docstring_source.allure_report,
                has_test_case("test_pytest_marker_with_kwargs_example",
                              has_tag("marker(stuff='cool')")
                              )
                )


def test_pytest_marker_with_kwargs_native_encoding(executed_docstring_source):
    """
    >>> import pytest

    >>> @pytest.mark.marker(stuff='я')
    ... def test_pytest_marker_with_kwargs_native_encoding_example():
    ...     pass
    """

    assert_that(executed_docstring_source.allure_report,
                has_test_case("test_pytest_marker_with_kwargs_native_encoding_example",
                              has_tag("marker(stuff=%s)" % represent('я'))
                              )
                )


def test_pytest_marker_with_kwargs_utf_encoding(executed_docstring_source):
    """
    >>> import pytest

    >>> @pytest.mark.marker(stuff=u'я')
    ... def test_pytest_marker_with_kwargs_utf_encoding_example():
    ...     pass
    """

    assert_that(executed_docstring_source.allure_report,
                has_test_case("test_pytest_marker_with_kwargs_utf_encoding_example",
                              has_tag("marker(stuff=%s)" % represent('я'))
                              )
                )
