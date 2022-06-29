from setuptools import setup, find_packages

from som import VERSION

setup(
    name="som",
    version=VERSION,
    packages=find_packages(
        exclude=[
            "test",
            "test.*"
        ]
    ),
    package_data={
    },
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'somrun = som.som_runner:main'
        ]
    }
)