from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='aws-cost-calculator-cli',
    version='2.1.0',
    packages=['cost_calculator'],
    install_requires=[
        'click>=8.0.0',
        'boto3>=1.26.0',
        'requests>=2.28.0',
    ],
    entry_points={
        'console_scripts': [
            'cc=cost_calculator.cli:cli',
        ],
    },
    author='Cost Optimization Team',
    author_email='',
    description='AWS Cost Calculator CLI - Calculate daily and annual AWS costs across multiple accounts',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/trilogy-group/aws-cost-calculator',
    project_urls={
        'Documentation': 'https://github.com/trilogy-group/aws-cost-calculator/blob/main/README.md',
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Monitoring',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.8',
    keywords='aws cost calculator billing optimization cloud',
)
