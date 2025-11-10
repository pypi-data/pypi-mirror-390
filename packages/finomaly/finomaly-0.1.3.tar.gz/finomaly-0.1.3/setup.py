from setuptools import setup, find_packages

setup(
    name="finomaly",
    version="0.1.3",
    author="Barisaksel",
    description="A rule-based and machine learning-based anomaly detection library for financial transactions.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "scikit-learn",
        "numpy",
        "fpdf",
        "matplotlib",
        "seaborn",
        "pandas",
        "xgboost"
    ],
    python_requires=">=3.8",
    project_urls={
        "Source": "https://github.com/Barisaksel/finomaly",
        "PyPI": "https://pypi.org/project/finomaly/",
        # "Documentation": "https://github.com/Barisaksel/finomaly#readme"  # Uncomment if you have a docs site
    },
)
