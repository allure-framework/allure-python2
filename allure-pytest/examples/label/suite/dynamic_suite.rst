Dynamic suite
-------------------

Also suites can be dynamically updated from within test body using allure.dynamic.suite.


    >>> import allure

    >>> def test_dynamic_suite():
    ...     allure.dynamic.suite("Dynamic suite")
    ...     allure.dynamic.parent_suite("Dynamic suite")
    ...     allure.dynamic.sub_suite("Dynamic suite")
