#!/usr/bin/env python
# SPDX-License-Identifier: Apache-2.0
import os
import pathlib #
from typing import List
from setuptools import find_packages, setup

#ROOT_DIR = os.path.dirname(__file__)
ROOT_DIR = pathlib.Path(__file__).parent.resolve()


def get_path(*filepath) -> str:
    return os.path.join(ROOT_DIR, *filepath)


def get_requirements() -> List[str]:
    """Get Python package dependencies from requirements.txt."""
    requirements_path = ROOT_DIR / "requirements.txt"
    print(f"requirements_path: {requirements_path}")
    def _read_requirements(filename: str) -> List[str]:
        #with open(get_path(filename)) as f:
        with open(requirements_path) as f:
            requirements = f.read().strip().split("\n")
        resolved_requirements = []
        for line in requirements:
            if line.startswith("-r "):
                resolved_requirements += _read_requirements(line.split()[1])
            elif line.startswith("--"):
                continue
            else:
                resolved_requirements.append(line)
        return resolved_requirements

    try:
        requirements = _read_requirements("requirements.txt")
    except ValueError:
        print("Failed to read requirements.txt in vllm_tpu.")
    return requirements


print("Start the set up"),
print(f"Current directory: {pathlib.Path('.').resolve()}")
print(f"ROOT_DIR: {ROOT_DIR}")

setup(
    name="test-ylang",
    version=os.environ.get('VERSION'),
    description="",
    long_description=open("README.md").read() if hasattr(
        open("README.md"), "read") else "",
    long_description_content_type="text/markdown",
    author="tpu_commons Contributors",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=get_requirements(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
print("Setup script finished.")
