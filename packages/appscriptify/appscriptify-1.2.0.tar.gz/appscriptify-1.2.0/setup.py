from setuptools import setup, find_packages

setup(
    name="appscriptify",
    version="1.2.0",
    author="Vansh Choyal",
    description="AppScriptify CLI — create app templates instantly",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "appscriptify=appscriptify.__main__:main",
        ],
    },
    python_requires=">=3.6",
    license='MIT',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://appscriptify.com'
)
