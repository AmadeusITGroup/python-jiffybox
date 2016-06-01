# coding=utf-8

from codecs import open
import re
import sys

from setuptools import setup


def strip_ref_directives(text):
    def cb(match):
        group = match.group(0)
        return group.split('`', 1)[1].rsplit('<', 1)[0].strip()

    return re.sub(r':ref:`[^`]+`', cb, text)


with open('README.rst', 'r', 'utf-8') as f:
    readme = f.read()
with open('CHANGES.rst', 'r', 'utf-8') as f:
    changes = f.read()


needs_pytest = set(['pytest', 'test']).intersection(sys.argv)
setup_requires = ['pytest-runner'] if needs_pytest else []

install_requires = [
    'requests',
    'six',
]
cli_requires = [
    'click',
    'visitor>=0.1.3',
]
tests_require = ['pytest', 'requests_mock', 'pytest-runner']
tests_require.extend(install_requires)
tests_require.extend(cli_requires)

setup(name='jiffybox',
      version='0.11.0',
      description='API wrapper for jiffybox.de',
      long_description=strip_ref_directives(
          readme + '\n\n' + changes,
      ),
      author='Amadeus IT Group',
      author_email='opensource@amadeus.com',
      maintainer='Thomas Weißschuh',
      maintainer_email='thomas.weissschuh@de.amadeus.com',
      url='https://github.com/AmadeusITGroup/python-jiffybox',
      packages=['jiffybox'],
      license='GPL3',
      keywords='API jiffybox domainfactory',
      zip_safe=True,
      install_requires=install_requires,
      extras_require={
          'cli': cli_requires,
          'tests': tests_require,
      },
      setup_requires=setup_requires,
      tests_require=tests_require,
      entry_points='''
      [console_scripts]
      jiffybox=jiffybox.cli:jiffybox
      ''',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      )
