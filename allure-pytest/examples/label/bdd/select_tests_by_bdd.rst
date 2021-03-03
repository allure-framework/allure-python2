Selecting tests by BDD label
----------------------------

You can use following commandline options to specify different sets of tests to execute passing a list of
comma-separated values:

--allure-epics
--allure-features
--allure-stories

There are some tests marked with BDD labels:

    >>> import allure

    >>> @allure.epic("My Epic")
    ... @allure.feature("My Feature")
    ... @allure.story("My Story")
    ... def test_with_epic_feature_story():
    ...     pass


    >>> @allure.epic("My Epic")
    ... @allure.feature("My Feature")
    ... def test_with_epic_feature():
    ...     pass


    >>> @allure.epic("My Epic")
    ... def test_with_epic():
    ...     pass


    >>> @allure.epic("Another Epic")
    ... @allure.feature("Another Feature")
    ... @allure.story("Another Story")
    ... def test_with_another_epic_feature_story():
    ...     pass

* If you run ``pytest`` with following options::

    $ pytest tests.py --allure-epics=My Epic --alluredir=./report

  first three tests will be runned.

* And with next options::

    $ pytest tests.py --allure-stories=My Story, Another Story --alluredir=./report

  it will run just are first and last test.

* If set ``--allure-labels-exclusive`` option, you also can run test by several labels specified::

    $ pytest tests.py --allure-labels-exclusive --allure-epics=My Epic --allure-features=My Feature --alluredir=./report

  it will run only first two tests.
