from setuptools import setup, find_packages

setup(
    name="Essentiax",  # ✅ match your PyPI name exactly (case-insensitive)
    version="0.1.6",
  # ⬆️ increment version number (important!)
    author="Shubham Wagh",
    author_email="waghshubham197@gmail.com",
    description="A next-generation Python library for smart EDA, cleaning, and interpretability in ML.",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/Essentiax/",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
        "matplotlib",
        "seaborn",
        "scikit-learn"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)

