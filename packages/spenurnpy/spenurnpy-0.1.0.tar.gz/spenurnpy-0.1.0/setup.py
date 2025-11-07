from setuptools import setup, find_packages

setup(
    name="spenurnpy",
    version="0.1.0",
    author="S P Ecialise Srinivasan",
    author_email="youremail@example.com",
    description="A collection of data preprocessing, clustering, and machine learning educational tools.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/nurnpy",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib",
        "scikit-learn",
        "scipy",
    ],
    python_requires=">=3.8",
)
