from functools import wraps

from allure_commons._core import plugin_manager
from allure_commons.types import LabelType, LinkType
from allure_commons.utils import uuid4, func_parameters, represent, StepFailMark


def safely(result):
    if result:
        return result[0]
    else:
        def dummy(function):
            return function
        return dummy


def title(test_title):
    return safely(plugin_manager.hook.decorate_as_title(test_title=test_title))


def description(test_description):
    return safely(plugin_manager.hook.decorate_as_description(test_description=test_description))


def description_html(test_description_html):
    return safely(plugin_manager.hook.decorate_as_description_html(test_description_html=test_description_html))


def label(label_type, *labels):
    return safely(plugin_manager.hook.decorate_as_label(label_type=label_type, labels=labels))


def severity(severity_level):
    return label(LabelType.SEVERITY, severity_level)


def epic(*epics):
    return label(LabelType.EPIC, *epics)


def feature(*features):
    return label(LabelType.FEATURE, *features)


def story(*stories):
    return label(LabelType.STORY, *stories)


def suite(suite_name):
    return label(LabelType.SUITE, suite_name)


def parent_suite(parent_suite_name):
    return label(LabelType.PARENT_SUITE, parent_suite_name)


def sub_suite(sub_suite_name):
    return label(LabelType.SUB_SUITE, sub_suite_name)


def tag(*tags):
    return label(LabelType.TAG, *tags)


def id(id):
    return label(LabelType.ID, id)


def link(url, link_type=LinkType.LINK, name=None):
    return safely(plugin_manager.hook.decorate_as_link(url=url, link_type=link_type, name=name))


def issue(url, name=None):
    return link(url, link_type=LinkType.ISSUE, name=name)


def testcase(url, name=None):
    return link(url, link_type=LinkType.TEST_CASE, name=name)


class Dynamic(object):

    @staticmethod
    def title(test_title):
        plugin_manager.hook.add_title(test_title=test_title)

    @staticmethod
    def description(test_description):
        plugin_manager.hook.add_description(test_description=test_description)

    @staticmethod
    def description_html(test_description_html):
        plugin_manager.hook.add_description_html(test_description_html=test_description_html)

    @staticmethod
    def label(label_type, *labels):
        plugin_manager.hook.add_label(label_type=label_type, labels=labels)

    @staticmethod
    def severity(severity_level):
        Dynamic.label(LabelType.SEVERITY, severity_level)

    @staticmethod
    def feature(*features):
        Dynamic.label(LabelType.FEATURE, *features)

    @staticmethod
    def story(*stories):
        Dynamic.label(LabelType.STORY, *stories)

    @staticmethod
    def tag(*tags):
        Dynamic.label(LabelType.TAG, *tags)

    @staticmethod
    def link(url, link_type=LinkType.LINK, name=None):
        plugin_manager.hook.add_link(url=url, link_type=link_type, name=name)

    @staticmethod
    def issue(url, name=None):
        Dynamic.link(url, link_type=LinkType.ISSUE, name=name)

    @staticmethod
    def testcase(url, name=None):
        Dynamic.link(url, link_type=LinkType.TEST_CASE, name=name)


def step(title):
    if callable(title):
        return StepContext(title.__name__, {})(title)
    else:
        return StepContext(title, {})


class StepContext:

    def __init__(self, title, params):
        self.title = title
        self.params = params
        self.uuid = uuid4()
        self.fail_mark = ''

    def __enter__(self):
        plugin_manager.hook.start_step(uuid=self.uuid, title=self.title, params=self.params)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _exc_type = exc_type
        _exc_val = exc_val

        if exc_type is None and self.fail_mark:
            _exc_type = StepFailMark
            _exc_val = StepFailMark(self.fail_mark)

        plugin_manager.hook.stop_step(uuid=self.uuid, title=self.title, exc_type=_exc_type, exc_val=_exc_val,
                                      exc_tb=exc_tb)

    def __call__(self, func):
        @wraps(func)
        def impl(*a, **kw):
            __tracebackhide__ = True
            params = func_parameters(func, *a, **kw)
            args = list(map(lambda x: represent(x), a))
            with StepContext(self.title.format(*args, **params), params):
                return func(*a, **kw)
        return impl


class Attach(object):

    def __call__(self, body, name=None, attachment_type=None, extension=None):
        plugin_manager.hook.attach_data(body=body, name=name, attachment_type=attachment_type, extension=extension)

    def file(self, source, name=None, attachment_type=None, extension=None):
        plugin_manager.hook.attach_file(source=source, name=name, attachment_type=attachment_type, extension=extension)


attach = Attach()


class fixture(object):
    def __init__(self, fixture_function, parent_uuid=None, name=None):
        self._fixture_function = fixture_function
        self._parent_uuid = parent_uuid
        self._name = name if name else fixture_function.__name__
        self._uuid = uuid4()
        self.parameters = None

    def __call__(self, *args, **kwargs):
        self.parameters = func_parameters(self._fixture_function, *args, **kwargs)

        with self:
            return self._fixture_function(*args, **kwargs)

    def __enter__(self):
        plugin_manager.hook.start_fixture(parent_uuid=self._parent_uuid,
                                          uuid=self._uuid,
                                          name=self._name,
                                          parameters=self.parameters)

    def __exit__(self, exc_type, exc_val, exc_tb):
        plugin_manager.hook.stop_fixture(parent_uuid=self._parent_uuid,
                                         uuid=self._uuid,
                                         name=self._name,
                                         exc_type=exc_type,
                                         exc_val=exc_val,
                                         exc_tb=exc_tb)


class test(object):
    def __init__(self, _test, context):
        self._test = _test
        self._uuid = uuid4()
        self.context = context
        self.parameters = None

    def __call__(self, *args, **kwargs):
        self.parameters = func_parameters(self._test, *args, **kwargs)

        with self:
            return self._test(*args, **kwargs)

    def __enter__(self):
        plugin_manager.hook.start_test(parent_uuid=None,
                                       uuid=self._uuid,
                                       name=None,
                                       parameters=self.parameters,
                                       context=self.context)

    def __exit__(self, exc_type, exc_val, exc_tb):
        plugin_manager.hook.stop_test(parent_uuid=None,
                                      uuid=self._uuid,
                                      name=None,
                                      context=self.context,
                                      exc_type=exc_type,
                                      exc_val=exc_val,
                                      exc_tb=exc_tb)
