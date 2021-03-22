Feature: Attachments

  Scenario: Attachment in called fixture
    Given example.feature with content:
      """
      Feature: Feature Test
        Scenario: My Scenario Test
          Given passed step
          When when-step use fixture, that have attachment
          Then passed step
      """
    And py file with name: example_test
    And with imports: pytest, pytest_bdd, allure
    And with passed steps
    And with func:
      """
      @pytest.fixture()
      def fixture_with_attachment():
          allure.attach('Attachment content', 'allure attachment', allure.attachment_type.TEXT)
      """
    And with func:
      """
      @pytest_bdd.when("when-step use fixture, that have attachment")
      def step_with_attachment(fixture_with_attachment):
          pass
      """
    And test for My Scenario Test from example.feature
    And py file saved

    When run pytest-bdd with allure

    Then attachment allure attachment must be in attachments
    And this attachment with content:
      """
      Attachment content
      """
    And attachments must not be in When when-step use fixture, that have attachment