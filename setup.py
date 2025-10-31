"""Module installing qstl_instruments"""
import shutil
import os
from setuptools import setup, find_namespace_packages, Command

class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        shutil.rmtree("build", ignore_errors=True)
        print("Removed build")
        egg_info = [f for f in os.listdir(".") if f.endswith(".egg-info")]
        for folder in egg_info:
            shutil.rmtree(folder, ignore_errors=True)
            print(f"Removed {folder}")

requirements = [
]
console_scripts = [
]

dependency_links = [
]

setup(
    name="qstl_instruments",
    version="0.1",
    author="QSTL",
    entry_points={
        "console_scripts": console_scripts,
    },
    install_requires=requirements,
    dependency_links=dependency_links,
    packages=find_namespace_packages(exclude=[]),
    description=("QSTL Instrument Drivers"),
    long_description="QSTL Instrument Drivers",
    long_description_content_type="text/markdown",
    url="https://github.com/alexist2623/QSTL_Instruments.git",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Window",
        "Operating System :: POSIX :: Linux"
    ],
    cmdclass={
        'clean': CleanCommand,
    },
    include_package_data=True
)