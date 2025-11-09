from setuptools import setup, find_packages

setup(
    name="geteddytor_django",
    use_scm_version=True, 
    version="0.1.0",
    setup_requires=["setuptools_scm"],
    packages=find_packages(),
    include_package_data=True,
    license="MIT License",
    description="A Django form widget for Eddytor rich text editor.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="",
    author="Buzzerboy",
    author_email="sales@usedrafty.com",
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
