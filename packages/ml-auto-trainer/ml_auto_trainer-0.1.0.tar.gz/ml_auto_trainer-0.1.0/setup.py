from setuptools import setup, find_packages

setup(
    name="ml_auto_trainer",
    version="0.1.0",
    author="Shivam Vinod Chaudhari",
    author_email="shivam7744998850@gmail.com",
    description="A simple auto machine learning trainer that builds models with one function call.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/shivchaudhari-ai/ml_auto_trainer",
    packages=find_packages(),
    install_requires=[
        "scikit-learn",
        "pandas",
        "xgboost",
        "numpy"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
