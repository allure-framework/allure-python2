from pytest_bdd import scenario


@scenario("links_features\\link_issue_test_case_link.feature", "Default link")
def test_default_link():
    pass


@scenario("links_features\\link_issue_test_case_link.feature", "Issue link")
def test_issue_link():
    pass


@scenario("links_features\\link_issue_test_case_link.feature", "Test case link")
def test_test_case_link():
    pass


@scenario("links_features\\link_without_name.feature", "Link without name")
def test_link_without_name():
    pass


@scenario("links_features\\all_links_type.feature", "All links type")
def test_all_links_type():
    pass
