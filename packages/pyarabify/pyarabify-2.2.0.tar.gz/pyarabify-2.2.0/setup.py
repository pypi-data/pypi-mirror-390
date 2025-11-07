from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='pyarabify',
    version='2.0.0',
    author='MERO',
    author_email='',
    description='مكتبة قوية لتحويل لغة Python كاملة إلى العربية مع دعم اللهجات المختلفة',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/6x-u/pyarabify',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'pyarabify': [
            'dat/*.json',
            'src/*.py'
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Topic :: Software Development :: Interpreters',
        'Topic :: Software Development :: Localization',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Natural Language :: Arabic',
        'Operating System :: OS Independent',
    ],
    python_requires='>=2.7',
    entry_points={
        'console_scripts': [
            'pyarabify=pyarabify.__main__:main',
        ],
    },
    keywords='arabic python interpreter localization translation عربي بايثون',
    project_urls={
        'Bug Reports': 'https://github.com/6x-u/pyarabify/issues',
        'Source': 'https://github.com/6x-u/pyarabify',
        'Telegram': 'https://t.me/QP4RM',
    },
)
