import os
import re
from setuptools import setup, find_packages


with open('gmailsync/__init__.py', 'r') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        f.read(), re.MULTILINE).group(1)
if not version:
    raise RuntimeError('Cannot find version information')


with open('README.md', 'r') as f:
    readme = f.read()


with open('requirements.txt', 'r') as f:
    requires = f.read().split()


setup(
    name='gmailsync',
    version=version,
    description='Synchronize and save a backup of your Gmail messages.',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Alberto Alcolea',
    author_email='albertoalcolea@gmail.com',
    url='http://albertoalcolea.com',
    license='Apache 2.0',
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    entry_points={
        'console_scripts': [
            'gmailsync = gmailsync.__main__:main'
        ]
    },
    classifiers=(
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Communications :: Email',
        'Topic :: Communications :: Email :: Email Clients (MUA)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
    ),
)
