from pytest_bdd import scenario


@scenario("labels_features\\tag_in_gherkin_or_scenario.feature",
          "Tag in gherkin")
def test_tag_in_gherkin():
    pass


@scenario("labels_features\\tag_in_gherkin_or_scenario.feature",
          "Tag in scenario")
def test_tag_in_scenario():
    pass


@scenario("labels_features\\tags_in_gherkin_and_scenario.feature",
          "Different tag in gherkin and scenario")
def test_different_tags():
    pass


@scenario("labels_features\\tags_in_gherkin_and_scenario.feature",
          "Same tag in gherkin and scenario")
def test_same_tags():
    pass


@scenario("labels_features\\many_tags.feature",
          "Many tags in gherkin")
def test_many_tags_in_gherkin():
    pass


@scenario("labels_features\\many_tags.feature",
          "Many tags in scenario")
def test_many_tags_in_scenario():
    pass


@scenario("labels_features\\many_tags.feature",
          "Many tags in gherkin and scenario")
def test_many_tags_in_gherkin_and_scenario():
    pass


@scenario("labels_features\\tags_in_feature.feature",
          "Tag in feature")
def test_tag_in_feature():
    pass
