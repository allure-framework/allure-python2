Feature: Attachments

  Scenario: Attachment in many steps
    Given example.feature with content:
      """
      Feature: Feature Test
        Scenario: My Scenario Test
          Given given step with attach
          When when step with attach
          Then then step with attach
      """
    And py file with name: example_test
    And with imports: pytest_bdd, allure
    And with passed steps
    And with func:
      """
      @pytest_bdd.given("given step with attach")
      def given_step_with_attachment():
          allure.attach('Given Attachment content', 'given allure attachment', allure.attachment_type.TEXT)
      """
    And with func:
      """
      @pytest_bdd.when("when step with attach")
      def when_step_with_attachment():
          allure.attach('When Attachment content', 'when allure attachment', allure.attachment_type.TEXT)
      """
    And with func:
      """
      @pytest_bdd.then("then step with attach")
      def then_step_with_attachment():
          allure.attach('Then Attachment content', 'then allure attachment', allure.attachment_type.TEXT)
      """
    And test for My Scenario Test from example.feature
    And py file saved

    When run pytest-bdd with allure

    Then attachment given allure attachment must be in Given given step with attach
    And this attachment with content:
      """
      Given Attachment content
      """
    And attachment when allure attachment must be in When when step with attach
    And this attachment with content:
      """
      When Attachment content
      """
    And attachment then allure attachment must be in Then then step with attach
    And this attachment with content:
      """
      Then Attachment content
      """
