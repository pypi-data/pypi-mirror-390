from setuptools import setup, find_packages

setup(
    name="Lambda-REST-Client",
    version="0.1.0.1",            
    author="Armen-Jean Andreasian",
    author_email="armen.andreasian.dev@proton.me",
    description="A simple client for calling Lambda REST endpoints",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/a-jean-andreasian/Lambda-REST-Client",
    packages=find_packages(exclude=["tests", "docs"]),
    python_requires=">=3.8",
    install_requires=[
        "aiohappyeyeballs==2.6.1",
        "aiohttp==3.13.2",
        "aiosignal==1.4.0",
        "attrs==25.4.0",
        "frozenlist==1.8.0",
        "idna==3.11",
        "multidict==6.7.0",
        "propcache==0.4.1",
        "yarl==1.22.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
)
