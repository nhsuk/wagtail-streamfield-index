from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

INSTALL_REQUIRES = ["django>=3.2", "Wagtail>=5.0.0", " wagtail < 7.0"]

TESTING_REQUIRES = ["pytest==6.2.5", "pytest-django==3.5.1", "pytest-pythonpath==0.7.3", "factory-boy>=3.2"]

LINTING_REQUIRES = ["black==25.1.0", "flake8==7.3.0", "flake8-black==0.3.6", "isort==6.0.1"]

setup(
    name="wagtail-streamfield-index",
    version="1.0.0",
    description="Indexing for Wagtail streamfields",
    author="Mike Monteith",
    author_email="<mike.monteith@nhs.net>",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nhsuk/wagtail-streamfield-index",
    install_requires=INSTALL_REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    extras_require={"testing": TESTING_REQUIRES, "linting": LINTING_REQUIRES},
)
