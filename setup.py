from setuptools import find_packages, setup

from masar_erp import __version__

setup(
    name="masar_erp",
    version=__version__,
    description="MASAR ERP custom application for Frappe",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
