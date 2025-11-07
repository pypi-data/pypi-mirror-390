import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

version = {}
with open("src/d4k_ms_auth/__info__.py") as fp:
  exec(fp.read(), version)

setuptools.setup(
    name="d4k_ms_auth",
    version=version['__package_version__'],
    author="D Iberson-Hurst",
    author_email="",
    description="A python package containing classes for microservice user interfces",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
       "auth0-python>=4.7.2", 
       "Authlib>=1.6.4", 
       "d4k_ms_base>=0.4.0",
       "fastapi>=0.121.0"
    ],
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    tests_require=["pytest", "pytest-cov", "pytest-mock", "pytest-asyncio"],
    python_requires=">=3.10",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
)
