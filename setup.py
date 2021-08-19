from setuptools import setup, find_packages

setup(
    name='servico_datastorage',
    version='1.0.1',
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['Flask', 'flask_cors', 'pymongo', 'pandas', 're']
)
