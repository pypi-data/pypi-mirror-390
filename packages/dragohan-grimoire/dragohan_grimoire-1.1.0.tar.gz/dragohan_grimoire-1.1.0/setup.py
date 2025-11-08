from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dragohan-grimoire",
    version="1.1.0",  # Version bump - added internet library
    py_modules=["json_mage", "simple_file"],  # Keep your existing modules
    packages=find_packages(),  # This will find the 'internet' package
    install_requires=[
        "jmespath>=1.0.0",
        "httpx>=0.27.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=5.0.0",
    ],
    author="DragoHan",
    author_email="aafr0408@gmail.com",
    description="AI Automation Grimoire - JSON, files & HTTP requests made dead simple",
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
    keywords="json, files, automation, api, data-processing, http, web-scraping",
)
