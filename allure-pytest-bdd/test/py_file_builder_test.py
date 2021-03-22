from .py_file_builder import PyFileBuilder
import pytest


def test_common_func():
    imports = ["pytest", "pytest_bdd", "allure"]
    funcs = [
        """@given("given_step")
def given_func():
    allure.attach("blah", ...)
    raise Exception("message")""",
        """@when("when_step")
def when_func():
    allure.attach("blah", ...)
    raise Exception("message")""",
        """@then("then_step")
def then_func():
    allure.attach("blah", ...)
    raise Exception("message")"""
    ]

    expected_answer = """import pytest
import pytest_bdd
import allure


@given("given_step")
def given_func():
    allure.attach("blah", ...)
    raise Exception("message")


@when("when_step")
def when_func():
    allure.attach("blah", ...)
    raise Exception("message")


@then("then_step")
def then_func():
    allure.attach("blah", ...)
    raise Exception("message")"""

    file_builder = PyFileBuilder("test")

    file_builder.add_imports(*imports)

    for func in funcs:
        file_builder.add_func(func)

    assert file_builder.get_content() == expected_answer


def test_without_imports_func():
    funcs = [
        """@given("given_step")
def given_func():
    allure.attach("blah", ...)
    raise Exception("message")""",
        """@when("when_step")
def when_func():
    allure.attach("blah", ...)
    raise Exception("message")""",
        """@then("then_step")
def then_func():
    allure.attach("blah", ...)
    raise Exception("message")"""
    ]

    expected_answer = """@given("given_step")
def given_func():
    allure.attach("blah", ...)
    raise Exception("message")


@when("when_step")
def when_func():
    allure.attach("blah", ...)
    raise Exception("message")


@then("then_step")
def then_func():
    allure.attach("blah", ...)
    raise Exception("message")"""

    file_builder = PyFileBuilder("test")

    file_builder.add_imports()

    for func in funcs:
        file_builder.add_func(func)

    assert file_builder.get_content() == expected_answer


def test_empty_func_str():
    funcs = [
        "",
        """@when("when_step")
def when_func():
    allure.attach("blah", ...)
    raise Exception("message")""",
        """@then("then_step")
def then_func():
    allure.attach("blah", ...)
    raise Exception("message")"""
    ]

    expected_answer = """


@when("when_step")
def when_func():
    allure.attach("blah", ...)
    raise Exception("message")


@then("then_step")
def then_func():
    allure.attach("blah", ...)
    raise Exception("message")"""

    file_builder = PyFileBuilder("test")

    file_builder.add_imports()

    for func in funcs:
        file_builder.add_func(func)

    assert file_builder.get_content() == expected_answer


def test_have_no_added_funcs():
    imports = ["pytest", "pytest_bdd", "allure"]
    funcs = []

    file_builder = PyFileBuilder("test")

    file_builder.add_imports(*imports)

    for func in funcs:
        file_builder.add_func(func)

    with pytest.raises(Exception):
        file_builder.get_content()
