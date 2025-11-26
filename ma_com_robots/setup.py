from setuptools import setup, find_packages

setup(
    name="ai2thor-object-locator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "ai2thor>=5.0.0",
        "prior>=0.1.0",
        "transformers>=4.35.2",
        "torch>=2.1.0",
        "sentence-transformers>=2.2.0",
    ],
    python_requires=">=3.10",
)
