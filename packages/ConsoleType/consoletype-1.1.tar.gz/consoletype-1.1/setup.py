from setuptools import setup, find_packages

setup(
    name='ConsoleType',
    version='1.1',
    packages=find_packages(),
    description='My Project',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Vadim | Mur Studio',
    author_email='somerare23@gmail.com',
    url='https://github.com/твой-аккаунт/твой-пакет',
    install_requires=[],
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8, <3.15"
)