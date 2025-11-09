from setuptools import setup, find_packages

setup(
    name='totopubsub',
    version='1.0.0',
    description='Agnostic PubSub implementation for Toto',
    author='nicolasances',
    author_email='nicolas.matteazzi@gmail.com',
    packages=find_packages(),
    install_requires=[
        "boto3", 
        "google-api-core",
        "google-auth",
        "google-cloud-core",
        "google-cloud-pubsub"
    ]
)
