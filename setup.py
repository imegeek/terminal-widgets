from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '1.25'
DESCRIPTION = 'A fully functional program for Terminal to show information about system, display, shell, package and many more.'

# Setting up
setup(
    name="terminal-widgets",
    version=VERSION,
    author="Im Geek (Ankush Bhagat)",
    author_email="<imegeek@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    entry_points={
        'console_scripts': ['twidgets = twidgets:main'],
    },
    packages=find_packages(),
    install_requires=["py-cpuinfo", "psutil", "rich", "rich-argparse", "requests"],
    keywords=['python', 'style', 'terminal', "widgets", "sysfetch"],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)