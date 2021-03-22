Feature: Attachments

  Scenario: Attachment and exception in step
    Given example.feature with content:
      """
      Feature: Feature Test
        Scenario: My Scenario Test
          Given step with attach and exception
          When passed step
          Then passed step
      """
    And py file with name: example_test
    And with imports: pytest_bdd, allure
    And with passed steps
    And with func:
      """
      @pytest_bdd.given("step with attach and exception")
      def step_with_attachment():
          allure.attach('Attachment content', 'allure attachment', allure.attachment_type.TEXT)
          raise Exception("Exception message")
      """
    And test for My Scenario Test from example.feature
    And py file saved

    When run pytest-bdd with allure

    Then attachment allure attachment must be in Given step with attach and exception
    And this attachment with content:
      """
      Attachment content
      """
