# setup.py
from setuptools import setup, find_packages

setup(
    name="house-price-model",
    version="0.1.0",
    author="Your Name",
    author_email="your_email@example.com",
    description="A trained machine learning model for predicting house prices",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pandas",
        "scikit-learn",
        "joblib",
        "numpy",
        "streamlit",
        "flask"    
        ],
    python_requires=">=3.8",
)
