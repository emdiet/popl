from setuptools import setup, find_packages

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='popl',
    version='0.1.4',
    description='A pip wrapper behaving like npm',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='emdiet',
    url='https://github.com/emdiet/popl',
    packages=find_packages(),
    py_modules=['popl'],
    entry_points={
        'console_scripts': [
            'popl=popl:main'
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7'
)