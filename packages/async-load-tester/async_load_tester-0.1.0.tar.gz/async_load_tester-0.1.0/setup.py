from setuptools import setup, find_packages
import os

# Read the README file for long description
with open('README.MD', 'r', encoding='utf-8') as f:
    long_description = f.read()

# Read requirements from a requirements.txt file if it exists, otherwise use defaults
def read_requirements():
    if os.path.exists('requirements.txt'):
        with open('requirements.txt', 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    else:
        return [
            'aiohttp>=3.7.0',
            'requests>=2.25.0',
            'python-dotenv>=0.15.0',
        ]

setup(
    name='py-loader',
    version='0.1.0',
    description='Asynchronous HTTP Load Testing Tool with Database Storage and Betterstack Integration',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Saptarshi Dutta',
    author_email='saptarshidutta2001@gmail.com',
    url='https://github.com/Saptarshi2001/pyload',
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements(),
    extras_require={
        'dev': [
            'pytest>=6.0.0',
            'pytest-asyncio>=0.14.0',
            'coverage>=5.0.0',
            'black>=21.0.0',
            'flake8>=3.8.0',
        ],
        'test': [
            'pytest>=6.0.0',
            'pytest-asyncio>=0.14.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'pyload=pyload:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        'Topic :: Software Development :: Testing :: Traffic Generation',
        'Topic :: System :: Benchmark',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
        'Framework :: AsyncIO',
    ],
    keywords='load-testing http async aiohttp performance monitoring betterstack',
    python_requires='>=3.7',
    project_urls={
        'Bug Reports': 'https://github.com/Saptarshi2001/pyload/issues',
        'Source': 'https://github.com/Saptarshi2001/pyload',
        'Documentation': 'https://github.com/Saptarshi2001/pyload#readme',
    },
)
