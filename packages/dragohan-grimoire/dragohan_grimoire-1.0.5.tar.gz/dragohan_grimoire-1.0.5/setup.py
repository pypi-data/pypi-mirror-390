from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dragohan-grimoire",
    version="1.0.5",  # Version bump for PyPI
    py_modules=["json_mage", "simple_file"],
    install_requires=[
        "jmespath>=1.0.0",
    ],
    author="DragoHan",
    author_email="aafr0408@gmail.com",  # Add your email
    description="AI Automation Grimoire - JSON mastery & file handling made dead simple",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/farhanistopG1/my_grimoire",
    project_urls={
        "Bug Tracker": "https://github.com/farhanistopG1/my_grimoire/issues",
        "Source Code": "https://github.com/farhanistopG1/my_grimoire",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    keywords="json, files, automation, api, data-processing",
)
