Feature: Attachments

  Scenario: Attachment in Given
    Given example.feature with content:
      """
      Feature: Feature Test
        Scenario: My Scenario Test
          Given step with attach
          When passed step
          Then passed step
      """
    And py file with name: example_test
    And with imports: pytest_bdd, allure
    And with passed steps
    And with func:
      """
      @pytest_bdd.given("step with attach")
      def step_with_attachment():
          allure.attach('Attachment content', 'allure attachment', allure.attachment_type.TEXT)
      """
    And test for My Scenario Test from example.feature
    And py file saved

    When run pytest-bdd with allure

    Then attachment allure attachment must be in Given step with attach
    And this attachment with content:
      """
      Attachment content
      """

  Scenario: Attachment in When
    Given example.feature with content:
      """
      Feature: Feature Test
        Scenario: My Scenario Test
          Given passed step
          When step with attach
          Then passed step
      """
    And py file with name: example_test
    And with imports: pytest_bdd, allure
    And with passed steps
    And with func:
      """
      @pytest_bdd.when("step with attach")
      def step_with_attachment():
          allure.attach('Attachment content', 'allure attachment', allure.attachment_type.TEXT)
      """
    And test for My Scenario Test from example.feature
    And py file saved

    When run pytest-bdd with allure

    Then attachment allure attachment must be in When step with attach
    And this attachment with content:
      """
      Attachment content
      """

  Scenario: Attachment in Then
    Given example.feature with content:
      """
      Feature: Feature Test
        Scenario: My Scenario Test
          Given passed step
          When passed step
          Then step with attach
      """
    And py file with name: example_test
    And with imports: pytest_bdd, allure
    And with passed steps
    And with func:
      """
      @pytest_bdd.then("step with attach")
      def step_with_attachment():
          allure.attach('Attachment content', 'allure attachment', allure.attachment_type.TEXT)
      """
    And test for My Scenario Test from example.feature
    And py file saved

    When run pytest-bdd with allure

    Then attachment allure attachment must be in Then step with attach
    And this attachment with content:
      """
      Attachment content
      """