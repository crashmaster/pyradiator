from datetime import datetime
from distutils.core import setup

from setuptools import find_packages


def get_date():
    now = datetime.now()
    return "{:04d}{:02d}{:02d}{:02d}{:02d}{:02d}".format(
        now.year,
        now.month,
        now.day,
        now.hour,
        now.minute,
        now.second
    )


PACKAGE_NAME = "pyradiator"
PACKAGE_VERSION = "0.1.{}".format(get_date())
PACKAGE_REQUIREMENTS = [
    "prettytable",
    "pygame",
    "requests",
]
DEPENDENCY_LINKS = [
    "hg+http://bitbucket.org/pygame/pygame#egg=pygame-dev",
]
AUTHOR = "Johnny Crash"
AUTHOR_EMAIL = "cannon.imus@gmail.com"
URL = "https://github.com/crashmaster/pyradiator"
CONSOLE_SCRIPTS = [
    "pyradiator = pyradiator.radiator:main",
]


setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    install_requires=PACKAGE_REQUIREMENTS,
    dependency_links=DEPENDENCY_LINKS,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    packages=find_packages(),
    entry_points={
        "console_scripts": CONSOLE_SCRIPTS,
    }
)
