import allure_commons
import pytest
from .utils import ALLURE_LINK_MARK


class AllureTestHelper(object):
    def __init__(self, config):
        self.config = config

    @allure_commons.hookimpl
    def decorate_as_link(self, url, link_type, name):
        pattern = dict(self.config.option.allure_link_pattern).get(link_type, u'{}')
        url = pattern.format(url)
        allure_link = getattr(pytest.mark, ALLURE_LINK_MARK)
        name = url if name is None else name
        return allure_link(url, name=name, link_type=link_type)
