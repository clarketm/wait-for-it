import setuptools

from wait_for_it import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wait-for-it",
    version=__version__,
    author="Travis Clarke",
    author_email="travis.m.clarke@gmail.com",
    description="Wait for service(s) to be available before executing a command.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/clarketm/wait-for-it",
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    setup_requires=["setuptools>=38.6.0"],  # for long_description_content_type
    py_modules=["wait_for_it"],
    install_requires=["click"],
    extras_require={"dev": ["black", "click", "flake8", "parameterized", "pytest", "pytest-cov", "twine"]},
    entry_points={"console_scripts": ["wait-for-it=wait_for_it.wait_for_it:cli"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Topic :: Internet",
        "Topic :: Utilities",
    ],
)
