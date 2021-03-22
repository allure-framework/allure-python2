Feature: Labels

  Scenario: Different tag in gherkin and scenario
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
    And with func:
      """
      @pytest.mark.another_tag
      @pytest_bdd.scenario("example.feature", "My Scenario Test")
      def test_scenario():
          pass
      """
    And py file saved

    When run pytest-bdd with allure

    Then tag test_tag is present in the report
    And tag another_tag is present in the report

    Scenario: Same tag in gherkin and scenario
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