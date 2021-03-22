Feature: Labels

  Scenario: Tag in gherkin
    Given example.feature with content:
      """
      Feature: Feature Test
        @test_tag
        Scenario: My Scenario Test
          Given passed step
          When passed step
          Then passed step
      """
    And py file with name: example_test
    And with imports: pytest, pytest_bdd, allure
    And with passed steps
    And test for My Scenario Test from example.feature
    And py file saved

    When run pytest-bdd with allure

    Then tag test_tag is present in the report

    Scenario: Tag in scenario
    Given example.feature with content:
      """
      Feature: Feature Test
        Scenario: My Scenario Test
          Given passed step
          When passed step
          Then passed step
      """
    And py file with name: example_test
    And with imports: pytest, pytest_bdd, allure
    And with passed steps
    And with func:
      """
      @pytest.mark.test_tag
      @pytest_bdd.scenario("example.feature", "My Scenario Test")
      def test_scenario():
          pass
      """
    And py file saved

    When run pytest-bdd with allure

    Then tag test_tag is present in the report