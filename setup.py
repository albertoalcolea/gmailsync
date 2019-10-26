import os
import re
from setuptools import setup


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
    author='Alberto Alcolea',
    author_email='albertoalcolea@gmail.com',
    url='http://albertoalcolea.com',
    license='Apache 2.0',
    packages=['gmailsync'],
    package_dir={'gmailsync': 'gmailsync'},
    package_data={
        'gmailsync': ['README.md', 'LICENSE']
    },
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    entry_points={
        'console_scripts': [
            'gmailsync = gmailsync.__main__:main'
        ]
    },
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
    ),
)
