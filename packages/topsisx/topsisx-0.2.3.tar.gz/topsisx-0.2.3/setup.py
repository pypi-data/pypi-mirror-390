from setuptools import setup, find_packages

# Read the long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="topsisx",
    version="0.2.3",
    author="Suvit Kumar",
    author_email="suvitkumar03@gmail.com",
    description="A Python library for Multi-Criteria Decision Making (TOPSIS, AHP, VIKOR, Entropy) with Web Interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SuvitKumar003/ranklib",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'topsisx': ['app.py'],
    },
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "matplotlib>=3.8.0",
        "streamlit>=1.34.0",
        "fpdf>=1.7.2",
    ],
    extras_require={
        'api': [
            'fastapi>=0.110.0',
            'uvicorn>=0.23.0',
        ],
        'dev': [
            'pytest>=8.2.0',
            'flake8>=7.0.0',
            'black>=24.3.0',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "topsisx=topsisx.cli:main",  # Main CLI command
        ],
    },
    keywords=[
        "mcdm",
        "topsis",
        "ahp",
        "vikor",
        "entropy",
        "decision-making",
        "multi-criteria",
        "operations-research",
        "optimization",
    ],
    project_urls={
        "Bug Reports": "https://github.com/SuvitKumar003/ranklib/issues",
        "Source": "https://github.com/SuvitKumar003/ranklib",
        "Documentation": "https://github.com/SuvitKumar003/ranklib/blob/main/README.md",
    },
)