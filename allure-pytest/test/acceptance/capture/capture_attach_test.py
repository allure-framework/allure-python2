import pytest
from hamcrest import assert_that
from hamcrest import all_of, is_, is_not, empty
from hamcrest import has_property, has_value
from hamcrest import contains_string


@pytest.mark.parametrize("capture", ["sys", "fd", "no"])
def test_capture_stdout(allured_testdir, capture):
    """
    >>> import pytest
    >>> import allure

    >>> @pytest.fixture
    ... def fixture(request):
    ...     print ("Start fixture")
    ...     def finalizer():
    ...         print ("Stop fixture")
    ...     request.addfinalizer(finalizer)

    >>> def test_capture_stdout_example(fixture):
    ...     print ("Start test")
    ...     with allure.step("Step"):
    ...         print ("Start step")
    """

    allured_testdir.parse_docstring_source()
    allured_testdir.run_with_allure("--capture={capture}".format(capture=capture))

    if_pytest_capture_ = is_not if capture == "no" else is_

    assert_that(allured_testdir.allure_report,
                has_property("attachments",
                             all_of(
                                 if_pytest_capture_(has_value(contains_string("Start fixture"))),
                                 if_pytest_capture_(has_value(contains_string("Stop fixture"))),
                                 if_pytest_capture_(has_value(contains_string("Start test"))),
                                 if_pytest_capture_(has_value(contains_string("Start step")))
                             )
                             )
                )


@pytest.mark.parametrize("capture", ["sys", "fd"])
def test_capture_empty_stdout(allured_testdir, capture):
    """
    >>> import pytest
    >>> import allure

    >>> @pytest.fixture
    ... def fixture(request):
    ...     def finalizer():
    ...         pass
    ...     request.addfinalizer(finalizer)

    >>> def test_capture_stdout_example(fixture):
    ...     with allure.step("Step"):
    ...         pass
    """

    allured_testdir.parse_docstring_source()
    allured_testdir.run_with_allure("--capture={capture}".format(capture=capture))

    assert_that(allured_testdir.allure_report,
                has_property("attachments", empty())
                )


@pytest.mark.parametrize("logging", [True, False])
def test_capture_log(allured_testdir, logging):
    """
    >>> import logging
    >>> import pytest
    >>> import allure

    >>> logger = logging.getLogger(__name__)

    >>> @pytest.fixture
    ... def fixture(request):
    ...     logger.info("Start fixture")
    ...     def finalizer():
    ...         logger.info("Stop fixture")
    ...     request.addfinalizer(finalizer)

    >>> def test_capture_log_example(fixture):
    ...     logger.info("Start test")
    ...     with allure.step("Step"):
    ...         logger.info("Start step")
    """

    allured_testdir.parse_docstring_source()

    params = [] if logging else ["-p", "no:logging"]
    if_logging_ = is_ if logging else is_not

    allured_testdir.run_with_allure("--log-cli-level=INFO", *params)

    assert_that(allured_testdir.allure_report,
                has_property("attachments",
                             all_of(
                                 if_logging_(has_value(contains_string("Start fixture"))),
                                 if_logging_(has_value(contains_string("Stop fixture"))),
                                 if_logging_(has_value(contains_string("Start test"))),
                                 if_logging_(has_value(contains_string("Start step")))
                             )
                             )
                )


def test_capture_disabled(allured_testdir):
    """
    >>> import logging
    >>> logger = logging.getLogger(__name__)

    >>> def test_capture_disabled_example():
    ...     logger.info("Start logging")
    ...     print ("Start printing")

    """

    allured_testdir.parse_docstring_source()
    allured_testdir.run_with_allure("--log-cli-level=INFO", "--allure-no-capture")

    assert_that(allured_testdir.allure_report,
                has_property("attachments", empty())
                )


def test_capture_passed_disabled_for_successful(allured_testdir):
    """
    >>> import logging
    >>> logger = logging.getLogger(__name__)

    >>> def test_capture_passed_disabled_example():
    ...     logger.info("Start logging")
    ...     print ("Start printing")

    """

    allured_testdir.parse_docstring_source()
    allured_testdir.run_with_allure("--log-cli-level=INFO", "--allure-no-capture-passed")

    assert_that(allured_testdir.allure_report,
                has_property("attachments", empty())
                )


def test_capture_passed_disabled_for_unsuccessful(allured_testdir):
    """
    >>> import logging
    >>> logger = logging.getLogger(__name__)

    >>> def test_capture_passed_disabled_example():
    ...     logger.info("Start logging")
    ...     print ("Start printing")
    ...     assert False

    """

    allured_testdir.parse_docstring_source()
    allured_testdir.run_with_allure("--log-cli-level=INFO", "--allure-no-capture-passed")

    assert_that(allured_testdir.allure_report,
                has_property("attachments",
                             all_of(
                                 is_(has_value(contains_string("Start logging"))),
                                 is_(has_value(contains_string("Start printing")))
                             )
                             )
                )
