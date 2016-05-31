# coding=utf-8

from codecs import open

from setuptools import setup

with open('README.rst', 'r', 'utf-8') as f:
    readme = f.read()
with open('CHANGES.rst', 'r', 'utf-8') as f:
    changes = f.read()

setup(name='jiffybox',
      version='0.10.0',
      description='API wrapper for jiffybox.de',
      long_description=readme + '\n\n' + changes,
      author='Amadeus IT Group',
      author_email='opensource@amadeus.com',
      maintainer='Thomas Weißschuh',
      maintainer_email='thomas.weissschuh@de.amadeus.com',
      url='https://github.com/AmadeusITGroup/python-jiffybox',
      packages=['jiffybox'],
      license='GPL3',
      keywords='API jiffybox domainfactory',
      zip_safe=True,
      install_requires=[
          'requests',
          'six',
      ],
      extras_require={
          'cli': [
              'click',
              'visitor>=0.1.3',
          ],
      },
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
