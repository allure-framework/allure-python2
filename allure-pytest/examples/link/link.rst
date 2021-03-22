Links
-----

    >>> import allure

    >>> @allure.link("http://qameta.io")
    >>> def test_link():
    ...     pass


    >>> @allure.issue("https://github.com/allure-framework/allure-python/issues/24")
    ... def test_issue_link():
    ...    pass


    >>> @allure.testcase("issues/24#issuecomment-277330977")
    ... def test_testcase_link():
    ...     pass


    >>> @allure.link("http://qameta.io", name="QAMETA", link_type="homepage")
    ... def test_custom_link():
    ...     pass

    >>> import pytest
    >>> @allure.link("{link}")
    >>> @pytest.mark.parametrize("test, link", [(True, 'link/666'), (False, 'link/777')])
    >>> def test_parametrize_link(test, link):
    ...     assert test

    >>> @allure.issue("{issue}")
    >>> @allure.testcase("{testcase}")
    >>> @pytest.mark.parametrize("test, issue, testcase", [(True, 'issues/666', 'testcase/666'), (False, 'issues/777', 'testcase/777')])
    >>> def test_parametrize_link_multiple(test, issue, testcase):
    ...     assert test