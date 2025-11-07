from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fortigate-cert-decoder",
    version="1.0.1",
    author="Todd Albiston",
    author_email="foxtrot711@gmail.com",
    description="A CLI tool for retrieving and decoding certificates from FortiGate devices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/fortigate-cert-decoder",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Networking :: Firewalls",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.28.0",
        "cryptography>=41.0.0",
        "rich>=13.0.0",
        "urllib3>=1.26.0",
    ],
    entry_points={
        "console_scripts": [
            "fgt-cert-decode=fortigate_cert_decoder.cert_decode:main",
        ],
    },
    keywords="fortigate certificate ssl tls decoder x509 firewall",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/fortigate-cert-decoder/issues",
        "Source": "https://github.com/yourusername/fortigate-cert-decoder",
    },
)
