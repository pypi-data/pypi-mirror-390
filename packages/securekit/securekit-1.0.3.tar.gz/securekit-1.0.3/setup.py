from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="securekit",
    version="1.0.3",
    author="SecureKit Team",
    author_email="anshumansingh3697@gmail.com",
    description="Production-ready cryptography library for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/anshuman365/securekit",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9", 
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "argon2-cffi>=21.3.0",
        "cryptography>=41.0.0",
        "pynacl>=1.5.0",
    ],
    extras_require={
        "aws": ["boto3>=1.28.0"],
        "vault": ["hvac>=1.1.0"], 
        "django": ["Django>=3.2.0"],
        "flask": ["Flask>=2.0.0"],
        "fastapi": ["fastapi>=0.68.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0", 
            "bandit>=1.7.0",
            "safety>=2.0.0",
        ],
    },
    entry_points={
        "securekit.cli": [
            "main = securekit.cli.main:main",
        ],
    },
)
