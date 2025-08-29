from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

INSTALL_REQUIRES = ["django>=3.2", "Wagtail>=5.0.0", " wagtail < 7.0"]

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
