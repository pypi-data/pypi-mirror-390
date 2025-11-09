from setuptools import setup, find_packages
import os

# Baca README dengan encoding UTF-8
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md"), "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="streamlit_launcher",
    version="4.0.0",
    author="Dwi Bakti N Dev",
    author_email="dwibakti76@gmail.com",
    description=(
        "Streamlit Launcher is an advanced no-code platform that integrates Streamlit, "
        "deep learning, and machine learning into one unified environment. "
        "It allows users to train models, visualize data, and perform complete statistical "
        "and analytical tasks effortlessly without writing any code. With powerful AI-driven "
        "automation, it simplifies complex workflows for research, health, and data science."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/royhtml",
    project_urls={
        "Profile": "https://profiledwibaktindev.netlify.app/",
        "Itch.io": "https://royhtml.itch.io/",
        "Facebook": "https://www.facebook.com/Royhtml",
        "Webtoons": "https://www.webtoons.com/id/canvas/mariadb-hari-senin/episode-4-coding-championship/viewer?title_no=1065164&episode_no=4",
        "Global Komik": "https://globalcomix.com/read/dc7f0116-7187-49a0-a27b-62b6c81eb435/1?utm_medium=GCMobileReaderApp&utm_source=share-release&utm_campaign=Royy&utm_term=122186",
        "Portfolio": "https://portofolio-dwi-bakti-n-dev-liard.vercel.app/",
        "Download": "https://pepy.tech/projects/streamlit-launcher?timeRange=threeMonths&category=version&includeCIDownloads=true&granularity=daily&viewType=line&versions=3.8.7%2C3.8.5%2C3.7.9"
    },
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "pillow>=8.0,<11.0",
        "pyinstaller>=4.0,<7.0",
        "pyqt5>=5.15,<6.0",
        "streamlit>=1.0,<2.0",
        "numpy>=1.21,<2.0",
        "pandas>=1.3,<3.0",
        "scikit-learn>=1.0,<2.0",
        "matplotlib>=3.4,<4.0",
        "seaborn>=0.11,<1.0",
        "tensorflow>=2.6,<3.0",
        "torch>=1.9,<3.0",
        "plotly>=5.0,<7.0",
        "openpyxl>=3.0,<4.0",
        "scipy>=1.7,<2.0",
        "joblib>=1.1,<2.0",
        "requests>=2.25,<3.0",
        "opencv-python>=4.5",
        "keras>=2.6",
        "xgboost>=1.5",
        "lightgbm>=3.3",
        "catboost>=1.0",
        "statsmodels>=0.13",
        "networkx>=2.6",
        "pyarrow>=5.0",
        "sphinx>=4.0",
        "sphinx-rtd-theme>=1.0",
        "sphinx-autodoc-typehints>=1.0",
        "pytest>=6.0",
        "pytest-cov>=2.0",
        "black>=21.0",
        "flake8>=3.9",
        "mypy>=0.910",
        "pre-commit>=2.0"
    ],
    entry_points={
        "gui_scripts": [
            "streamlit_launcher=streamlit_launcher.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "webscan": ["*.ico", "*.png"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Software Development :: User Interfaces",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Education",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.7",
)
