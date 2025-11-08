from setuptools import setup, find_packages
import os

# Read the contents of your README file
with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

# Read requirements from requirements.txt
with open('requirements.txt', 'r', encoding='utf-8') as fh:
    requirements = fh.read().splitlines()

# Get package version from __init__.py
def get_version():
    package_init = os.path.join(os.path.dirname(__file__), 'monei', '__init__.py')
    with open(package_init, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip("'\"")
    return '0.1.0'

setup(
    name='monei',
    version=get_version(),
    author='Monei Team',
    author_email='tech@monei.cc',
    description='Official Python SDK for Monei API - Financial services, wallets, and crypto exchange',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Mr-Money01/monei-python-sdk',
    packages=find_packages(include=['monei', 'monei.*']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Office/Business :: Financial',
        'Topic :: Internet :: WWW/HTTP',
    ],
    python_requires='>=3.8',
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-asyncio>=0.21.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'isort>=5.12.0',
            'mypy>=1.0.0',
            'flake8>=6.0.0',
            'pre-commit>=3.0.0',
        ],
        'docs': [
            'sphinx>=7.0.0',
            'sphinx-rtd-theme>=1.0.0',
            'myst-parser>=2.0.0',
        ],
    },
    keywords=[
        'monei',
        'api',
        'sdk',
        'payments',
        'crypto',
        'wallet',
        'blockchain',
        'ethereum',
        'solana',
        'defi',
        'financial',
        'banking',
    ],
    project_urls={
        'Homepage': 'https://monei.cc',
        'Documentation': 'https://api.monei.cc/api-gateway-docs',
        'Repository': 'https://github.com/Mr-Money01/monei-python-sdk',
        'Issues': 'https://github.com/Mr-Money01/monei-python-sdk/issues',
        'Changelog': 'https://github.com/Mr-Money01/monei-python-sdk/releases',
    },
    license='MIT',
    include_package_data=True,
    zip_safe=False,
)