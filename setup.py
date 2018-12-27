import io
import os
from setuptools import setup, find_packages


def read(filename):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with io.open(filepath, mode='r', encoding='utf-8') as f:
        return f.read()


setup(
    name='pytest-board',
    version='0.1.0',
    description='Local continuous test runner with pytest and watchdog.',
    long_description=read('README.md'),
    author='Jaeman An',
    author_email='ajmbell@gmail.com',
    url='http://github.com/kuss/pytest-board',
    license='MIT',
    platforms='any',
    packages=find_packages(),
    install_requires=read('requirements.txt').splitlines(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'pytest-board= pytest_board:main',
            'ptb = pytest_board:main',
        ]
    },
)
