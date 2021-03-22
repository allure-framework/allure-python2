Feature: Labels

  Scenario: Many tags in gherkin
    Given example.feature with content:
      """
      Feature: Feature Test
        @test_tag_1 @test_tag_2
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

    Then tag test_tag_1 is present in the report
    And tag test_tag_2 is present in the report

    Scenario: Many tags in scenario
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
      @pytest.mark.test_tag_1
      @pytest.mark.test_tag_2
      @pytest_bdd.scenario("example.feature", "My Scenario Test")
      def test_scenario():
          pass
      """
    And py file saved

    When run pytest-bdd with allure

    Then tag test_tag_1 is present in the report
    And tag test_tag_2 is present in the report

    Scenario: Many tags in gherkin and scenario
    Given example.feature with content:
      """
      Feature: Feature Test
        @test_tag_1 @test_tag_2
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
      @pytest.mark.test_tag_3
      @pytest.mark.test_tag_4
      @pytest_bdd.scenario("example.feature", "My Scenario Test")
      def test_scenario():
          pass
      """
    And py file saved

    When run pytest-bdd with allure

    Then tag test_tag_1 is present in the report
    And tag test_tag_2 is present in the report
    And tag test_tag_3 is present in the report
    And tag test_tag_4 is present in the report
