import pytest
import allure

BODY = ['I Like to', 'Move It']


def say_function(string):
    print(string)
    return string


class TestFromTest(object):
    def test_print_from_test(self, saying):
        """
        >>> allure_report = getfixture('allure_report')
        >>> assert_that(allure_report,
        ...             has_test_case('test_print_from_test',
        ...                           has_attachment(attach_type='text/plain', name='test log')
        ...             ))
        """
        print(saying)

    def test_no_print_from_test(self):
        """
        >>> allure_report = getfixture('allure_report')
        >>> assert_that(allure_report,
        ...             has_test_case('test_no_print_in_test',
        ...                           has_no_attachment()
        ...             ))
        """
        pass

    def test_print_from_function(self, saying):
        """
        >>> allure_report = getfixture('allure_report')
        >>> assert_that(allure_report,
        ...             has_test_case('test_print_from_function',
        ...                           has_attachment(attach_type='text/plain', name='test log')
        ...             ))
        """
        say_function(saying)

    def test_many_print(self, saying):
        """
        >>> allure_report = getfixture('allure_report')
        >>> assert_that(allure_report,
        ...             has_test_case('test_many_print',
        ...                           has_attachment(attach_type='text/plain', name='test log')
        ...             ))
        """
        say_function(saying)
        print(saying)

    def test_print_from_step(self, saying):
        """
        >>> allure_report = getfixture('allure_report')
        >>> assert_that(allure_report,
        ...             has_test_case('test_print_from_step',
        ...                           all_of(has_attachment(attach_type='text/plain', name='test log'),
        ...                                  has_step('Step with print',
        ...                                            all_of(has_attachment(name='step log')
        ...                                                   has_step('Nested step with print',
        ...                                                             has_attachment(name='step log')
        ...                                                   )
        ...                                            )
        ...                                  )
        ...                            )
        ...             )
        ... )
        """
        with allure.step('Step with print'):
            print(saying)
            with pytest.allure.step('Nested step with print'):
                say_function(saying)

    @pytest.mark.parametrize('attachment', BODY)
    def test_print_from_parametrized_test(self, say):
        """
        >>> allure_report = getfixture('allure_report')
        >>> for say in BODY:
        ...     assert_that(allure_report,
        ...                 has_test_case('test_print_from_parametrized_test[{body}]'.format(body=say),
        ...                              has_attachment(name='step log')
        ...                )
        ...     )
        """
        print(say)


class TestFromFixture(object):

    # def test_print_from_fixture(saying_fixture):
    #     return saying_fixture
    #
    # PARAMS = ["first", "second", "third"]
    #
    # @pytest.fixture(scope='module', params=PARAMS)
    # def attach_data_in_parametrized_fixture(request):
    #     allure.attach(request.param, name=request.param, attachment_type='text/plain')
    #
    # TEXT = "attachment body"

    @pytest.fixture
    def say_in_function_scope_fixture(self, saying):
        print(saying)
        return saying

    @pytest.fixture
    def say_in_function_scope_finalizer(self, saying, request):
        def fin():
            print(saying)

        request.addfinalizer(fin)
        return saying

    @pytest.fixture(scope='module')
    def say_in_module_scope_fixture(self):
        string = 'module saying'
        print(string)
        return string

    @pytest.fixture(scope='module')
    def say_in_module_scope_finalizer(request):
        string = 'module saying in finalizer'

        def fin():
            print(string)

        request.addfinalizer(fin)
        return string

    def test_print_in_function_scope_fixture(self, say_in_function_scope_fixture):
        """
        >>> allure_report = getfixture('allure_report')
        >>> assert_that(allure_report,
        ...             has_test_case('test_print_in_function_scope_fixture',
        ...                           has_container(allure_report,
        ...                                         has_before('say_in_function_scope_fixture',
        ...                                                     has_attachment(name='fixture log')
        ...                                         )
        ...                           )
        ...             )
        ... )
        """
        pass

    def test_print_in_function_scope_finalizer(self, say_in_function_scope_finalizer):
        """
        >>> allure_report = getfixture('allure_report')
        >>> assert_that(allure_report,
        ...             has_test_case('test_print_in_function_scope_finalizer',
        ...                           has_container(allure_report,
        ...                                         has_after('say_in_function_scope_finalizer::fin',
        ...                                                     has_attachment(name='fixture log')
        ...                                         )
        ...                           )
        ...             )
        ... )
        """
        pass

    def test_print_in_module_scope_fixture(say_in_module_scope_fixture):
        """
        >>> allure_report = getfixture('allure_report')
        >>> assert_that(allure_report,
        ...             has_test_case('test_print_in_module_scope_fixture',
        ...                           has_container(allure_report,
        ...                                        has_before('say_in_module_scope_fixture',
        ...                                                     has_attachment(name='fixture log')
        ...                                        )
        ...                           )
        ...             )
        ... )
        """
        pass

    def test_attach_data_in_module_scope_finalizer(say_in_module_scope_finalizer):
        """
        >>> allure_report = getfixture('allure_report')
        >>> assert_that(allure_report,
        ...             has_test_case('test_attach_data_in_module_scope_finalizer',
        ...                           has_container(allure_report,
        ...                                        has_after('{fixture}::{finalizer}'.format(
        ...                                                                    fixture='say_in_module_scope_finalizer',
        ...                                                                    finalizer='fin'),
        ...                                                     has_attachment(name='fixture log')
        ...                                        )
        ...                           )
        ...             )
        ... )
        """
        pass
