import os
import sys
from setuptools import setup, find_packages
from setuptools.command.install import install
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel


class bdist_wheel(_bdist_wheel):
    def finalize_options(self):
        _bdist_wheel.finalize_options(self)
        self.root_is_pure = False

    def get_tag(self):
        python, abi, plat = 'py2.py3', 'none', 'any'
        return python, abi, plat


class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        setup_dir = os.path.dirname(os.path.realpath(__file__))
        post_install_script = os.path.join(setup_dir, 'setup', 'post_install.py')
        os.system(f"{sys.executable} {post_install_script}")

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="azpype",
    version="0.4.1",
    description="A native Python interface wrapping AzCopy for bulk data transfer to and from Azure Blob Storage.",
    long_description=open('README.md', encoding="UTF-8").read(),
    long_description_content_type='text/markdown',
    url="https://github.com/yusuf-jkhan1/azpype",
    author="Yusuf Khan",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3"
    ],
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    package_data={
        # Include all files in the setup/assets/bin directory
        '': ['setup/assets/bin/*/*', 'setup/assets/bin/*/*.exe'],
    },
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'azpype-init=azpype.setup:main',
        ],
    },
    cmdclass={
        'bdist_wheel': bdist_wheel
    }
)