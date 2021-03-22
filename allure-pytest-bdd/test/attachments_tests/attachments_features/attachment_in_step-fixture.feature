Feature: Attachment

  Scenario: attachment in a step, that is also a fixture
    Given example.feature with content:
      """
      Feature: Feature Test
        Scenario: My Scenario Test
          Given passed step
          When when-step is fixture with attachment
          Then passed step using fixture
      """
    And py file with name: example_test
    And with imports: pytest, pytest_bdd, allure
    And with passed steps
    And with func:
      """
      @pytest.fixture()
      @pytest_bdd.when("when-step is fixture with attachment")
      def step_with_attachment():
          allure.attach('Attachment content', 'allure attachment', allure.attachment_type.TEXT)
      """
    And with func:
      """
      @pytest_bdd.then("passed step using fixture")
      def then_step(step_with_attachment):
          pass
      """
    And test for My Scenario Test from example.feature
    And py file saved

    When run pytest-bdd with allure

    Then attachment allure attachment must be in When when-step is fixture with attachment
    And this attachment with content:
      """
      Attachment content
      """
    And attachments must not be in attachments