# coding: utf-8

from setuptools import setup, find_packages  # noqa: H301

NAME = "ZSGF.Client"
VERSION = "2.1.4"
PYTHON_REQUIRES = ">= 3.8"
REQUIRES = [
    "urllib3 >= 1.25.3, < 3.0.0",
    "python-dateutil >= 2.8.2",
    "pydantic >= 2",
    "typing-extensions >= 4.7.1",
]

setup(
    name=NAME,
    version=VERSION,
    description="全部  API 文档",
    author="zashigaofa.com",
    author_email="noreply@zashigaofa.com",
    url="https://github.com/wz101010/zsgf-python",
    keywords=["zashigaofa","全部  API 文档"],
    install_requires=REQUIRES,
    packages=find_packages(exclude=["test", "tests"]),
    include_package_data=True,
    long_description_content_type='text/markdown',
    long_description="",
    package_data={"ZSGF.Client": ["py.typed"]},
)