
#python3 setup.py sdist bdist_wheel
from setuptools import setup,find_packages

setup(
    name="smssia",
    version='1.1.1',
    packages=find_packages(),
    install_requires=['pyperclip'],
)

