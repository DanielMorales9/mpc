from setuptools import setup, find_packages

with open('./requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="mpc",
    version="1.0.0",
    python_requires='>=3.7',
    packages=find_packages(),
    install_requires=requirements,
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3.7'
    ]
)