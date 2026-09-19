from setuptools import find_packages, setup

with open("requirements.txt") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="network-security-ml",
    version="0.1.0",
    description="Network Security ML project",
    author="",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.11",
)
