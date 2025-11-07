from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="testcase-converter",
    version="0.4.0",
    author="TestCaseConverter Contributors",
    author_email="testcase-converter@example.com",
    description="Convert test cases between Excel and XMind formats with enhanced features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/misldy/TestCaseConverter",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'testcase_converter': ['resources/*.xmind']
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Testing",
        "Topic :: Office/Business",
        "Intended Audience :: Developers"
    ],
    python_requires='>=3.7',
    install_requires=[
        'xmind',
        'openpyxl>=3.0.0',
        'dataclasses; python_version<"3.7"'
    ],
    entry_points={
        'console_scripts': [
            'testcase-converter=testcase_converter.converter:main'
        ]
    }
)