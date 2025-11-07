import json

from setuptools import setup, find_packages

with open("package_info.json", "r") as file:
    package_info = json.load(file)

package_name = package_info["package_name"].replace("-", "_")
package_version = package_info["package_version"]

with open("README.md", "r") as file:
    long_description = file.read()

with open("requirements.txt", "r") as file:
    requirements = [
        l.strip() for l in file.readlines() if not l.startswith("#") and l != "\n"
    ]

setup(
    name=package_name,
    version=package_version,
    description=package_name,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="TH2-devs",
    author_email="th2-devs@exactprosystems.com",
    url="https://github.com/th2-net/th2-data-services-utils",
    license="Apache License 2.0",
    python_requires=">=3.8",
    install_requires=requirements,
    packages=find_packages(include=['th2_data_services', 'th2_data_services.utils', 'th2_data_services.utils.pandas',
                                    'th2_data_services.utils.streams']),
    namespace_packages=['th2_data_services', 'th2_data_services.utils'],
    include_package_data=True,
)
