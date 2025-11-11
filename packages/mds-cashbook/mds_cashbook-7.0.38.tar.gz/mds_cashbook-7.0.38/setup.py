""" Tryton module to add a cashbook
"""

# Always prefer setuptools over distutils
from setuptools import setup
# To use a consistent encoding
from codecs import open
from os import path
import re
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

here = path.abspath(path.dirname(__file__))
MODULE = 'cashbook'
PREFIX = 'mds'

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# tryton.cfg einlesen
config = ConfigParser()
config.read_file(open('tryton.cfg'))
info = dict(config.items('tryton'))
for key in ('depends', 'extras_depend', 'xml'):
    if key in info:
        info[key] = info[key].strip().splitlines()

# Get module-versions
modversion = {}
with open(path.join(here, 'versiondep.txt'), encoding='utf-8') as f:
    l1 = f.readlines()
    for i in l1:
        l2 = i.strip().split(';')
        if len(l2) < 4:
            continue
        modversion[l2[0]] = {'min': l2[1], 'max': l2[2], 'prefix': l2[3]}

# tryton-version
major_version = 7
minor_version = 0

requires = ['python-slugify']
for dep in info.get('depends', []):
    if not re.match(r'(ir|res|webdav)(\W|$)', dep):
        if dep in modversion.keys():
            prefix = 'mds'
            if len(modversion[dep]['prefix']) > 0:
                prefix = modversion[dep]['prefix']

            if len(modversion[dep]['max']) > 0:
                requires.append('%s_%s >= %s, <= %s' % (
                    prefix, dep, modversion[dep]['min'],
                    modversion[dep]['max']))
            else:
                requires.append('%s_%s >= %s' % (
                    prefix, dep, modversion[dep]['min']))
        else:
            requires.append('%s_%s >= %s.%s, < %s.%s' % (
                'trytond', dep, major_version, minor_version,
                major_version, minor_version + 1))
requires.append('trytond >= %s.%s, < %s.%s' % (
    major_version, minor_version, major_version, minor_version + 1))

setup(
    name='%s_%s' % (PREFIX, MODULE),
    version=info.get('version', '0.0.1'),
    description='Tryton module to add a cashbook.',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://www.m-ds.de/',
    download_url='https://scmdev.m-ds.de/Tryton/Extra/cashbook',
    author='martin-data services',
    author_email='service@m-ds.de',
    license='GPL-3',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Framework :: Tryton',
        'Intended Audience :: Developers',
        'Intended Audience :: Customer Service',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Office/Business',
        'Topic :: Office/Business :: Financial :: Accounting',
        'Natural Language :: German',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],

    keywords='tryton cashbook',
    package_dir={'trytond.modules.%s' % MODULE: '.'},
    packages=[
        'trytond.modules.%s' % MODULE,
        ],
    package_data={
        'trytond.modules.%s' % MODULE: (info.get('xml', []) + [
            'tryton.cfg', 'locale/*.po', 'tests/*.py',
            'view/*.xml', 'icon/*.svg', 'docs/*.txt',
            'report/*.fods', 'versiondep.txt', 'README.rst']),
        },

    install_requires=requires,
    zip_safe=False,
    entry_points="""
    [trytond.modules]
    %s = trytond.modules.%s
    """ % (MODULE, MODULE),
)
