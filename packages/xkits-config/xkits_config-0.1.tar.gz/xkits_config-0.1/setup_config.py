# coding=utf-8

from urllib.parse import urljoin

from setuptools import setup
from setuptools.command.install import install

from xkits_config import __author__
from xkits_config import __author_email__
from xkits_config import __description__
from xkits_config import __project__
from xkits_config import __urlhome__
from xkits_config import __version__

__urlcode__ = __urlhome__
__urldocs__ = __urlhome__
__urlbugs__ = urljoin(__urlhome__, "issues")


def all_requirements():
    return [
        "xkits-lib>=0.4",
    ]


class CustomInstallCommand(install):
    """Customized setuptools install command"""

    def run(self):
        install.run(self)  # Run the standard installation
        # Execute your custom code after installation


setup(
    name=__project__,
    version=__version__,
    description=__description__,
    url=__urlhome__,
    author=__author__,
    author_email=__author_email__,
    project_urls={"Source Code": __urlcode__,
                  "Bug Tracker": __urlbugs__,
                  "Documentation": __urldocs__},
    py_modules=["xkits_config_annot", "xkits_config_class", "xkits_config"],
    install_requires=all_requirements(),
    cmdclass={
        "install": CustomInstallCommand,
    }
)
