from setuptools import setup, find_packages

setup(
    name="context-shield",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "textblob",
        "transformers",
        "torch",
    ],
    author="Your Name",
    description="AI tool for detecting toxic text and rewriting safely",
)
