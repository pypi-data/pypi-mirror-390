from setuptools import setup, find_packages


# README for long_description:
def read_readme():
    try:
        with open("README.md", "r", encoding = "utf-8") as f:
            return f.read()
    except:
        return "Python bindings for com0com virtual serial ports"


setup(
    name = "pycom0com",
    version = "1.0.2",
    packages = find_packages(),
    package_data = {
        "pycom0com": ["bin/*.*"],
    },
    install_requires = [],
    author = "StableKite",
    author_email = "stablekite@stablekite.com",
    url = "https://github.com/StableKite/pycom0com",
    description = "Python bindings for com0com virtual serial ports",
    long_description = read_readme(),
    long_description_content_type = "text/markdown",
    license = "GPL-2.0",
    keywords = "com0com serial virtual ports",
    classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12"
    ],
    python_requires = ">=3.7",
        entry_points = {
        "console_scripts": [
            "pycom0com-install=pycom0com._installer:main"  # Console command
        ],
    }
)