Feature: Links

  Scenario: Link without name
    Given example.feature with content:
      """
      Feature: Feature Test
        Scenario: My Scenario Test
          Given passed step
          When passed step
          Then passed step
      """
    And py file with name: example_test
    And with imports: pytest_bdd, allure
    And with passed steps
    And with func:
      """
      @allure.link('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
      @pytest_bdd.scenario("example.feature", "My Scenario Test")
      def test_scenario():
          pass
      """
    And py file saved

    When run pytest-bdd with allure

    Then report has link type of link with url:
      """
      https://www.youtube.com/watch?v=dQw4w9WgXcQ
      """