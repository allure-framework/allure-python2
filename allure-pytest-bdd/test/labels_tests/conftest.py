from pytest_bdd import then, parsers


@then(parsers.parse("tag {tag_name} is present in the report"))
def tag_is_present(tag_name, allure_report):
    tags_in_report = _get_tags_from_report(allure_report)
    assert tag_name in tags_in_report


@then(parsers.parse("tag {tag_name} is not present in the report"))
def tag_is_not_present(tag_name, allure_report):
    tags_in_report = _get_tags_from_report(allure_report)
    assert tag_name not in tags_in_report


def _get_tags_from_report(allure_report):
    test_case_report = allure_report.test_cases[0]
    return [label["value"] for label in test_case_report["labels"]
            if label["name"] == "tag"]
