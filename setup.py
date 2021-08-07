from setuptools import setup

with open("requirements.txt") as f:
    requirements = f.readlines()

setup(
    name="lima",
    version="0.0.1",
    author="pmbrull",
    description="Custom python interpreter",
    license="MIT",
    packages=["lima"],
    entry_points={"console_scripts": ["pylima=lima.shell:init"]},
    install_requires=requirements,
    zip_safe=False,
)
