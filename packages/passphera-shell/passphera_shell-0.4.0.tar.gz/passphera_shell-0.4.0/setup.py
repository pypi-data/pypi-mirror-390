from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='passphera-shell',
    version='0.4.0',
    author='Fathi Abdelmalek',
    author_email='passphera@imfathi.com',
    url='https://github.com/passphera/shell',
    description='The shell contain the use cases and interfaces of passphera project',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires='>=3',
    install_requires=['passphera-core', 'cryptography'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Security",
        "Topic :: Security :: Cryptography",
    ]
)
