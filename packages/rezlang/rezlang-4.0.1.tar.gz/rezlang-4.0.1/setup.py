from setuptools import setup, find_packages

setup(
    name="rezlang",
    version="4.0.1",
    author="Rez",
    author_email="justraih@example.com",
    description="RezLang+ — made by Rez",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/rez/rezlang",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="rezlang console effects fun animation",
)
