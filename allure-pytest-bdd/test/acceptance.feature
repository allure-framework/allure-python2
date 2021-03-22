# Created by denis at 11.01.2021
Feature: test
  # Enter feature description here

  Scenario: scenario
    Given py file with name: example
    And with imports: pytest, pytest_bdd, allure
    And with func:
      """
      @pytest_bdd.given("given_step")
      def my_func():
          allure.attach("blah", ...)
          raise Exception("message")
      """
    And test for scenario_name from file.feature
    And py file saved
