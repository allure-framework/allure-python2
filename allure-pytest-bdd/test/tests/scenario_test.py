from pytest_bdd import scenario


@scenario("../features/scenario.feature", "Simple passed scenario")
def test_simple_passed_scenario():
    pass
