from pytest_bdd import scenario, then


@scenario("bug474.feature", "allure.attach calling in function decorated with When and Pytest.fixture")
def test_my_scenario():
    pass
