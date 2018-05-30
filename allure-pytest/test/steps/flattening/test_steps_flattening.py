import allure


@allure.step("Function 1 has custom name")
def function1(a,b,c):
    pass


@allure.step
def function2(a,b,c):
    function1(1,2,3)


@allure.step(flatten=True)
def function3(a,b,c):
    function1(4,5,6)
    function2(7,8,9)


def test_flattened_steps():
    """
    >>> from allure_commons.utils import represent
    >>> allure_report = getfixture('allure_report')
    >>> assert_that(allure_report,
    ...             has_test_case('test_flattened_steps',
    ...                           has_step('First step',
    ...                                    has_step('Function 1 has custom name'),
    ...                                    has_step('function2',
    ...                                             has_step('Function 1 has custom name')
    ...                                    ),
    ...                                    has_step('function3',
    ...                                             not_( has_step('Function 1 has custom name') ),
    ...                                             not_( has_step('function2') ),
    ...                                    )
    ...                           ),
    ...                           has_step('Second step',
    ...                                    not_( has_step('Function 1 has custom name') ),
    ...                                    not_( has_step('function2') ),
    ...                                    has_step('Third step',
    ...                                             not_( has_step('function3') ),
    ...                                    ),
    ...                           )
    ...             )
    ... )
    """
    with allure.step("First step"):
        function1(1,1,1)
        function2(2,2,2)
        function3(3,3,3)

    with allure.step("Second step", flatten=True):
        function1(4,4,4)
        function2(5,5,5)

        with allure.step("Third step", force=True):
            function3(6,6,6)
