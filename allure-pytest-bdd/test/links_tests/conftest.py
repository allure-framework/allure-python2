from pytest_bdd import then, parsers


@then(parsers.parse(
    "report has link type of {type_name} with url:\n{url}"))
def check_link(type_name, url, allure_report):
    links = _get_links(allure_report)
    desired_link = {"type": type_name, "url": url, "name": url}

    assert desired_link in links


@then(parsers.parse(
    "report has link type of {type_name} with \"{link_name}\" name and url:\n{url}"))
def check_link_with_custom_name(type_name, link_name, url, allure_report):
    links = _get_links(allure_report)
    desired_link = {"type": type_name, "url": url, "name": link_name}

    assert desired_link in links


def _get_links(allure_report):
    return allure_report.test_cases[0]["links"]
