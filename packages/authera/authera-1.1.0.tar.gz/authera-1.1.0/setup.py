from setuptools import setup, find_packages

setup(
    name="",
    version="1.1.0",
    author="AlgoNouir",
    author_email="algo.mahdi.nouri@gmail.com",
    description="A modern authentication and user management package for Django (Clerk-style)",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/algonouire/authera",
    packages=find_packages(exclude=["tests*", "examples*"]),
    include_package_data=True,
    install_requires=[
        "Django>=4.2",
        "djangorestframework>=3.15",
		"djangorestframework-simplejwt>=5.3.0",
    ],
    python_requires=">=3.9",
    license="MIT",
    classifiers=[
        "Framework :: Django",
        "Framework :: Django :: 4.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="django authentication clerk jwt rest framework",
)
