# -*- coding: utf-8 -*-

import os
import sys
import six
import time
import uuid
import json
import socket
import inspect
import hashlib
import platform
import threading
import traceback
import collections

from functools import partial


def getargspec(func):
    """
    Used because getargspec for python 2.7 does not accept functools.partial
    which is the type for pytest fixtures.

    getargspec excerpted from:

    sphinx.util.inspect
    ~~~~~~~~~~~~~~~~~~~
    Helpers for inspecting Python modules.
    :copyright: Copyright 2007-2018 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.

    Like inspect.getargspec but supports functools.partial as well.
    """
    # noqa: E731 type: (Any) -> Any
    if inspect.ismethod(func):
        func = func.__func__
    parts = 0, ()  # noqa: E731 type: Tuple[int, Tuple[unicode, ...]]
    if type(func) is partial:
        keywords = func.keywords
        if keywords is None:
            keywords = {}
        parts = len(func.args), keywords.keys()
        func = func.func
    if not inspect.isfunction(func):
        raise TypeError('%r is not a Python function' % func)
    args, varargs, varkw = inspect.getargs(func.__code__)
    func_defaults = func.__defaults__
    if func_defaults is None:
        func_defaults = []
    else:
        func_defaults = list(func_defaults)
    if parts[0]:
        args = args[parts[0]:]
    if parts[1]:
        for arg in parts[1]:
            i = args.index(arg) - len(args)  # type: ignore
            del args[i]
            try:
                del func_defaults[i]
            except IndexError:
                pass
    return inspect.ArgSpec(args, varargs, varkw, func_defaults)  # type: ignore


if six.PY3:
    from traceback import format_exception_only
else:
    from _compat import format_exception_only


def md5(*args):
    m = hashlib.md5()
    for arg in args:
        part = arg.encode('utf-8')
        m.update(part)
    return m.hexdigest()


def uuid4():
    return str(uuid.uuid4())


def now():
    return int(round(1000 * time.time()))


def platform_label():
    major_version, _, __ = platform.python_version_tuple()
    implementation = platform.python_implementation()
    return '{implementation}{major_version}'.format(implementation=implementation.lower(),
                                                    major_version=major_version)


def thread_tag():
    return '{0}-{1}'.format(os.getpid(), threading.current_thread().name)


def host_tag():
    return socket.gethostname()


def escape_non_unicode_symbols(item):
    if not (six.PY2 and isinstance(item, str)):
        return item

    def escape_symbol(s):
        try:
            s.decode(encoding='UTF-8')
            return s
        except UnicodeDecodeError:
            return repr(s)[1:-1]

    return ''.join(map(escape_symbol, item))


def represent(item):
    """
    >>> represent(None)
    'None'

    >>> represent(123)
    '123'

    >>> import six
    >>> expected = u"'hi'" if six.PY2 else "'hi'"
    >>> represent('hi') == expected
    True

    >>> expected = u"'привет'" if six.PY2 else "'привет'"
    >>> represent(u'привет') == expected
    True

    >>> represent(bytearray([0xd0, 0xbf]))  # doctest: +ELLIPSIS
    "<... 'bytearray'>"

    >>> from struct import pack
    >>> result = "<type 'str'>" if six.PY2 else "<class 'bytes'>"
    >>> represent(pack('h', 0x89)) == result
    True

    >>> result = "<type 'int'>" if six.PY2 else "<class 'int'>"
    >>> represent(int) == result
    True

    >>> represent(represent)  # doctest: +ELLIPSIS
    '<function represent at ...>'

    >>> represent([represent])  # doctest: +ELLIPSIS
    '[<function represent at ...>]'

    >>> class ClassWithName(object):
    ...     pass

    >>> represent(ClassWithName)
    "<class 'utils.ClassWithName'>"
    """

    if six.PY2 and isinstance(item, str):
        try:
            item = item.decode(encoding='UTF-8')
        except UnicodeDecodeError:
            pass

    if isinstance(item, six.text_type):
        return u'\'%s\'' % item
    elif isinstance(item, (bytes, bytearray)):
        return repr(type(item))
    else:
        return repr(item)


def func_parameters(func, *args, **kwargs):
    """
    >>> def helper(func):
    ...     def wrapper(*args, **kwargs):
    ...         params = func_parameters(func, *args, **kwargs)
    ...         print(list(params.items()))
    ...         return func(*args, **kwargs)
    ...     return wrapper

    >>> @helper
    ... def args(a, b):
    ...     pass

    >>> args(1, 2)
    [('a', '1'), ('b', '2')]

    >>> args(*(1,2))
    [('a', '1'), ('b', '2')]

    >>> args(1, b=2)
    [('a', '1'), ('b', '2')]

    >>> @helper
    ... def kwargs(a=1, b=2):
    ...     pass

    >>> kwargs()
    [('a', '1'), ('b', '2')]

    >>> kwargs(a=3, b=4)
    [('a', '3'), ('b', '4')]

    >>> kwargs(b=4, a=3)
    [('a', '3'), ('b', '4')]

    >>> kwargs(a=3)
    [('a', '3'), ('b', '2')]

    >>> kwargs(b=4)
    [('a', '1'), ('b', '4')]

    >>> @helper
    ... def args_kwargs(a, b, c=3, d=4):
    ...     pass

    >>> args_kwargs(1, 2)
    [('a', '1'), ('b', '2'), ('c', '3'), ('d', '4')]

    >>> args_kwargs(1, 2, d=5)
    [('a', '1'), ('b', '2'), ('c', '3'), ('d', '5')]

    >>> args_kwargs(1, 2, 5, 6)
    [('a', '1'), ('b', '2'), ('c', '5'), ('d', '6')]

    >>> args_kwargs(1, b=2)
    [('a', '1'), ('b', '2'), ('c', '3'), ('d', '4')]

    >>> @helper
    ... def varargs(*a):
    ...     pass

    >>> varargs()
    []

    >>> varargs(1, 2)
    [('a', '(1, 2)')]

    >>> @helper
    ... def keywords(**a):
    ...     pass

    >>> keywords()
    []

    >>> keywords(a=1, b=2)
    [('a', '1'), ('b', '2')]

    >>> @helper
    ... def args_varargs(a, b, *c):
    ...     pass

    >>> args_varargs(1, 2)
    [('a', '1'), ('b', '2')]

    >>> args_varargs(1, 2, 2)
    [('a', '1'), ('b', '2'), ('c', '(2,)')]

    >>> @helper
    ... def args_kwargs_varargs(a, b, c=3, **d):
    ...     pass

    >>> args_kwargs_varargs(1, 2)
    [('a', '1'), ('b', '2'), ('c', '3')]

    >>> args_kwargs_varargs(1, 2, 4, d=5, e=6)
    [('a', '1'), ('b', '2'), ('c', '4'), ('d', '5'), ('e', '6')]

    >>> @helper
    ... def args_kwargs_varargs_keywords(a, b=2, *c, **d):
    ...     pass

    >>> args_kwargs_varargs_keywords(1)
    [('a', '1'), ('b', '2')]

    >>> args_kwargs_varargs_keywords(1, 2, 4, d=5, e=6)
    [('a', '1'), ('b', '2'), ('c', '(4,)'), ('d', '5'), ('e', '6')]

    >>> class Class(object):
    ...     @staticmethod
    ...     @helper
    ...     def static_args(a, b):
    ...         pass
    ...
    ...     @classmethod
    ...     @helper
    ...     def method_args(cls, a, b):
    ...         pass
    ...
    ...     @helper
    ...     def args(self, a, b):
    ...         pass

    >>> cls = Class()

    >>> cls.args(1, 2)
    [('a', '1'), ('b', '2')]

    >>> cls.method_args(1, 2)
    [('a', '1'), ('b', '2')]

    >>> cls.static_args(1, 2)
    [('a', '1'), ('b', '2')]

    """
    parameters = {}
    arg_spec = getargspec(func) if six.PY2 else inspect.getfullargspec(func)
    arg_order = list(arg_spec.args)
    args_dict = dict(zip(arg_spec.args, args))

    if arg_spec.defaults:
        kwargs_defaults_dict = dict(zip(arg_spec.args[-len(arg_spec.defaults):], arg_spec.defaults))
        parameters.update(kwargs_defaults_dict)

    if arg_spec.varargs:
        arg_order.append(arg_spec.varargs)
        varargs = args[len(arg_spec.args):]
        parameters.update({arg_spec.varargs: varargs} if varargs else {})

    if arg_spec.args and arg_spec.args[0] in ['cls', 'self']:
        args_dict.pop(arg_spec.args[0], None)

    if kwargs:
        if sys.version_info < (3, 6):
            # Sort alphabetically as old python versions does
            # not preserve call order for kwargs
            arg_order.extend(sorted(list(kwargs.keys())))
        else:
            # Keep py3.6 behaviour to preserve kwargs order
            arg_order.extend(list(kwargs.keys()))
        parameters.update(kwargs)

    parameters.update(args_dict)

    items = parameters.iteritems() if six.PY2 else parameters.items()
    sorted_items = sorted(map(lambda kv: (kv[0], represent(kv[1])), items), key=lambda x: arg_order.index(x[0]))

    return collections.OrderedDict(sorted_items)


def format_traceback(exc_traceback):
    return ''.join(traceback.format_tb(exc_traceback)) if exc_traceback else None


def format_exception(etype, value):
    """
    >>> import sys

    >>> try:
    ...     assert False, u'Привет'
    ... except AssertionError:
    ...     etype, e, _ = sys.exc_info()
    ...     format_exception(etype, e) # doctest: +ELLIPSIS
    'AssertionError: ...\\n'

    >>> try:
    ...     assert False, 'Привет'
    ... except AssertionError:
    ...     etype, e, _ = sys.exc_info()
    ...     format_exception(etype, e) # doctest: +ELLIPSIS
    'AssertionError: ...\\n'

    >>> try:
    ...    compile("bla u'Привет'", "fake.py", "exec")
    ... except SyntaxError:
    ...    etype, e, _ = sys.exc_info()
    ...    format_exception(etype, e) # doctest: +ELLIPSIS
    '  File "fake.py", line 1...SyntaxError: invalid syntax\\n'

    >>> try:
    ...    compile("bla 'Привет'", "fake.py", "exec")
    ... except SyntaxError:
    ...    etype, e, _ = sys.exc_info()
    ...    format_exception(etype, e) # doctest: +ELLIPSIS
    '  File "fake.py", line 1...SyntaxError: invalid syntax\\n'

    >>> from hamcrest import assert_that, equal_to

    >>> try:
    ...     assert_that('left', equal_to('right'))
    ... except AssertionError:
    ...     etype, e, _ = sys.exc_info()
    ...     format_exception(etype, e) # doctest: +ELLIPSIS
    "AssertionError: \\nExpected:...but:..."

    >>> try:
    ...     assert_that(u'left', equal_to(u'right'))
    ... except AssertionError:
    ...     etype, e, _ = sys.exc_info()
    ...     format_exception(etype, e) # doctest: +ELLIPSIS
    "AssertionError: \\nExpected:...but:..."
    """
    return '\n'.join(format_exception_only(etype, value)) if etype or value else None


def get_testplan():
    planned_tests = []
    file_path = os.environ.get("ALLURE_TESTPLAN_PATH")

    if file_path and os.path.exists(file_path):
        with open(file_path, 'r') as plan_file:
            plan = json.load(plan_file)
            planned_tests = plan.get("tests", [])

    return planned_tests
