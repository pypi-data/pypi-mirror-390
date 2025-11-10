from setuptools import setup, find_packages

setup(
    name="singular",
    version="1.0.0",
    py_modules=["singular"],
    packages=find_packages(),
    include_package_data=True,  # inclui templates, static, etc.
    install_requires=[
        "click",
        "jinja2",
        "werkzeug",
        "watchdog",
        "flask",
        
    ],
    entry_points={
        "console_scripts": [
            "singular=singular.cli:cli",
        ]
    }
)
