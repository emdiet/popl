from setuptools import setup, find_packages

setup(
    name='plp',
    version='0.1.0',
    description='A pip wrapper behaving like npm',
    author='emdiet',
    url='https://github.com/emdiet/plp',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'plp=plp:main'
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7'
)