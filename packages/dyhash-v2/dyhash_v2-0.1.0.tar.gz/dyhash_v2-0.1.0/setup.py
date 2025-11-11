from setuptools import setup, find_packages

setup(
    name="dyhash-v2",
    version="0.1.0",
    description="Advanced password analysis and hashing suite",
    author="Hady Hassan",
    packages=find_packages(),
    install_requires=[
        "bcrypt",
        "argon2-cffi"
    ],
    entry_points={
        "console_scripts": [
            "dyhash=dyhash.cli:main"
        ]
    },
    python_requires=">=3.8",
)