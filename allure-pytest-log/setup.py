import os, sys
from setuptools import setup
from pkg_resources import require, DistributionNotFound, VersionConflict

try:
    require('pytest-allure-adaptor')
    print("""
    You have pytest-allure-adaptor installed.
    You need to remove pytest-allure-adaptor from your site-packages
    before installing allure-pytest, or conflicts may result.
    """)
    sys.exit()
except (DistributionNotFound, VersionConflict):
    pass

PACKAGE = "allure-pytest-log"
VERSION = "0.1.0"

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Framework :: Pytest',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Topic :: Software Development :: Quality Assurance',
    'Topic :: Software Development :: Testing',
]

install_requires = [
    "allure-pytest>=2.4.1",
    "allure-python-commons>=2.4.1"
]


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def main():
    setup(
            name=PACKAGE,
            version=VERSION,
            description="Allure pytest integration with stdout capturing",
            url="https://github.com/allure-framework/allure-python-log",
            author="WuhuiZuo",
            author_email="wuhuizuo@126.com",
            license="Apache-2.0",
            classifiers=classifiers,
            keywords="allure reporting pytest output_capture",
            long_description=read('README.rst'),
            packages=["allure_pytest_log"],
            package_dir={"allure_pytest_log": "src"},
            entry_points={"pytest11": ["allure_pytest_log = allure_pytest_log.plugin"]},
            install_requires=install_requires
    )


if __name__ == '__main__':
    main()
