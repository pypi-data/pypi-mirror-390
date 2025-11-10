from setuptools import setup, find_packages

setup(
    name="tensorlaw",  # ✅ New package name
    version="1.0.1",
    author="tensorlaw",
    author_email="vivekmangiraj7@gmail.com",
    description="-",
    packages=find_packages(),
    include_package_data=True,
    package_data={"tensorlaw": ["**/*"]},  # ✅ Update package name here too
    license="MIT",
    python_requires=">=3.7",
)
