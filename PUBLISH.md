# How to Publish a Release

1. Increment the version number in [__init__.py](wait_for_it/__init__.py) using [semver] conventions:
    1. MAJOR version when you make incompatible API changes,
    1. MINOR version when you add functionality in a backwards compatible manner, and
    1. PATCH version when you make backwards compatible bug fixes. 

2. Build and upload the source distribution to staging – TestPyPI (Test Python Package Index):
```bash
# Run test, build the package, and upload to TestPyPI. 
make upload-test
```

3. Download the package and perform any manual qualification steps:
```bash
# Install from TestPyPI. 
make install-test
```

4. Build and upload the source distribution to production – PyPI (Python Package Index):
```bash
# Run tests, build the package, upload to PyPI, and publish a tagged GitHub release. 
make upload
```

5. Install and enjoy! 😀:
```bash
# Install from PyPI.  
make install
```

[semver]: https://semver.org/