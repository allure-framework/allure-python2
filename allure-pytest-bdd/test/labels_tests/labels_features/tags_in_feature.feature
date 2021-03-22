Feature: Labels

  Scenario: Tag in feature
    Given example.feature with content:
      """
      @test_tag
      Feature: Feature Test
        Scenario: My Scenario Test
          Given passed step
          When passed step
          Then passed step
      """
    And py file with name: example_test
    And with imports: pytest_bdd, allure
    And with passed steps
    And test for My Scenario Test from example.feature
    And py file saved

    When run pytest-bdd with allure

    Then tag test_tag is present in the report