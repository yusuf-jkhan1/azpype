from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="azpype",
    version="0.4.5",
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
        'azpype': ['assets/bin/*/*', 'assets/bin/*/*.exe', 'assets/config_templates/*.yaml'],
    },
    install_requires=requirements,
    cmdclass={}
)