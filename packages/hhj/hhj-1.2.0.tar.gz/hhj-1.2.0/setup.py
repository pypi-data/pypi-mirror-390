from setuptools import setup, find_packages

setup(
    name="hhj",
    version="1.2.0",
    description="See the repo on GitHub",
    author="NickC4p",
    author_email="postcodelab@gmail.com",
    packages=find_packages(where="hhj"),  
    package_dir={"": "hhj"},              
    entry_points={
        "console_scripts": [
            "hhj=hhj.__main__:main",     
        ],
    },
    python_requires=">=3.8",
    install_requires=[
        "pyyaml>=6.0.3",
        "requests>=2.32.5"
    ],
)
