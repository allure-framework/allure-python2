Feature: Attachments

  Scenario: Attachment in failed step
    Given example.feature with content:
      """
      Feature: Feature Test
        Scenario: My Scenario Test
          Given failed step with attach
          When passed step
          Then passed step
      """
    And py file with name: example_test
    And with imports: pytest_bdd, allure
    And with passed steps
    And with func:
      """
      @pytest_bdd.given("failed step with attach")
      def step_with_attachment():
          allure.attach('Attachment content', 'allure attachment', allure.attachment_type.TEXT)
          assert False
      """
    And test for My Scenario Test from example.feature
    And py file saved

    When run pytest-bdd with allure

    Then attachment allure attachment must be in Given failed step with attach
    And this attachment with content:
      """
      Attachment content
      """
