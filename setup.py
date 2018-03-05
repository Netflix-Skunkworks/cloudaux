"""
cloudaux
=====

Cloud Auxiliary is a python wrapper and orchestration module for interacting with cloud providers

:copyright: (c) 2016 by Netflix, see AUTHORS for more
:license: Apache, see LICENSE for more details.
"""
import sys
import os.path

from setuptools import setup, find_packages

ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__)))

# When executing the setup.py, we need to be able to import ourselves.  This
# means that we need to add the src/ directory to the sys.path

sys.path.insert(0, ROOT)

about = {}
with open(os.path.join(ROOT, "cloudaux", "__about__.py")) as f:
    exec(f.read(), about)

classifiers = [
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
]

install_requires = [
    'boto3>=1.5.20',
    'botocore>=1.8.34',
    'boto>=2.41.0',
    'joblib>=0.9.4',
    'inflection',
    'flagpole>=1.0.1',
    'defusedxml==0.5.0',
    'six>=1.11.0',
]

gcp_require = [
    'google-api-python-client>=1.6.1',
    'google-cloud-storage==0.22.0'
]

openstack_require = [
    'openstacksdk==0.9.18'
]

tests_require = [
    'pytest',
    'mock',
    'testtool'
]

docs_require = []

dev_require = []

setup(
    name=about["__title__"],
    version=about["__version__"],
    author=about["__author__"],
    author_email=about["__email__"],
    url=about["__uri__"],
    description=about["__summary__"],
    long_description=open(os.path.join(ROOT, 'README.md')).read(),
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    classifiers=classifiers,
    extras_require={
        'gcp': gcp_require,
        'openstack': openstack_require,
        'tests': tests_require,
        'docs': docs_require,
        'dev': dev_require
    }
)
