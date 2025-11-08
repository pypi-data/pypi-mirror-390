from setuptools import setup

setup(
    name="devcore-cli",
    version="1.0.2",
    author="Puji Ermanto | <Engineer>",
    author_email="puji@gmail.com",
    description="DevCore — WordPress & Laravel project automation CLI",
    py_modules=["devcore"],  # karena file kamu bernama devcore.py
    include_package_data=True,
    install_requires=[
        "jinja2>=3.1.2",
    ],
    entry_points={
        "console_scripts": [
            "devcore=devcore:main",  # ini akan panggil fungsi main() di devcore.py
        ],
    },
    python_requires=">=3.8",
)
