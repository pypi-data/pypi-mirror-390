from setuptools import setup, find_packages

setup(
    name="devcore-cli",
    version="1.0.3",
    author="Puji Ermanto | <Engineer>",
    author_email="puji@gmail.com",
    description="DevCore — WordPress & Laravel project automation CLI",
    packages=find_packages(include=["core", "core.*"]),
    py_modules=["devcore"],  # tetap sertakan devcore.py
    include_package_data=True,
    install_requires=[
        "jinja2>=3.1.2",
    ],
    entry_points={
        "console_scripts": [
            "devcore=devcore:main",
        ],
    },
    python_requires=">=3.8",
)
