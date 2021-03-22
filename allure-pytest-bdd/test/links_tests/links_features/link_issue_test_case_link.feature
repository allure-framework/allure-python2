Feature: Links

  Scenario: Default link
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
      @allure.link('https://www.youtube.com/watch?v=dQw4w9WgXcQ', name='Link')
      @pytest_bdd.scenario("example.feature", "My Scenario Test")
      def test_scenario():
          pass
      """
    And py file saved

    When run pytest-bdd with allure

    Then report has link type of link with "Link" name and url:
      """
      https://www.youtube.com/watch?v=dQw4w9WgXcQ
      """

  Scenario: Issue link
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
      @allure.issue('140', 'Issue')
      @pytest_bdd.scenario("example.feature", "My Scenario Test")
      def test_scenario():
          pass
      """
    And py file saved

    When run pytest-bdd with allure

    Then report has link type of issue with "Issue" name and url:
      """
      140
      """

  Scenario: Test case link
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
      @allure.testcase(
          'https://github.com/qameta/allure-integrations/issues/8#issuecomment-268313637',
          'Test case title')
      @pytest_bdd.scenario("example.feature", "My Scenario Test")
      def test_scenario():
          pass
      """
    And py file saved

    When run pytest-bdd with allure

    Then report has link type of test_case with "Test case title" name and url:
      """
      https://github.com/qameta/allure-integrations/issues/8#issuecomment-268313637
      """