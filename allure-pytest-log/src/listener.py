import pytest
import allure_commons
from allure_commons.types import AttachmentType
from allure_pytest.listener import ItemCache
from .utils import Tee


class AllureLogListener(object):

    def __init__(self, allure_listener=None):
        self.allure_listener = allure_listener
        self.modify_allure_listener(self.allure_listener)
        self._cache = allure_listener._cache
        self._tee_cache = TeeCache()

    def modify_allure_listener(self, listener):
        origin_start_before_fixture = listener.allure_logger.start_before_fixture
        origin_stop_before_fixture = listener.allure_logger.stop_before_fixture
        origin_start_after_fixture = listener.allure_logger.start_after_fixture
        origin_stop_after_fixture = listener.allure_logger.stop_after_fixture

        def start_before_fixture(parent_uuid, uuid, fixture):
            origin_start_before_fixture(parent_uuid, uuid, fixture)
            self.start_tee(uuid)

        def stop_before_fixture(uuid, **kwargs):
            self.finish_tee(uuid, 'fixture log')
            origin_stop_before_fixture(uuid, **kwargs)

        def start_after_fixture(parent_uuid, uuid, fixture):
            origin_start_after_fixture(parent_uuid, uuid, fixture)
            self.start_tee(uuid)

        def stop_after_fixture(uuid, **kwargs):
            self.finish_tee(uuid, 'fixture[after] log')
            origin_stop_after_fixture(uuid, **kwargs)

        listener.allure_logger.start_before_fixture = start_before_fixture
        listener.allure_logger.stop_before_fixture = stop_before_fixture
        listener.allure_logger.start_after_fixture = start_after_fixture
        listener.allure_logger.stop_after_fixture = stop_after_fixture

    def start_tee(self, uuid):
        tee = self._tee_cache.set(uuid)
        tee.start()

    def finish_tee(self, uuid, attach_name='log'):
        tee = self._tee_cache.pop(uuid)
        if not tee:
            return None
        try:
            self.allure_listener.allure_logger.attach_data(uuid,
                                                           body=tee.getvalue(),
                                                           name=attach_name,
                                                           attachment_type=AttachmentType.TEXT)
        finally:
            tee.close()

    @allure_commons.hookimpl(hookwrapper=True)
    def start_step(self, uuid, title, params):
        yield
        self.start_tee(uuid)

    @allure_commons.hookimpl(hookwrapper=True)
    def stop_step(self, uuid, exc_type, exc_val, exc_tb):
        self.finish_tee(uuid, 'step log')
        yield

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_call(self, item):
        uuid = self._cache.get(item.nodeid)
        self.start_tee(uuid)
        yield
        self.finish_tee(uuid, 'test log')


class TeeCache(ItemCache):
    def set(self, _id):
        return self._items.setdefault(str(_id), Tee())
