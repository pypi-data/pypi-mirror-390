from setuptools import setup, find_packages  # type: ignore
from pathlib import Path
__name__="QCPROGS"
__doc__="""QCPROGS is a comprehensive automated solution designed to streamline Excel
            and SQL data processing for promotion analysis. It includes tools for reading,
            transforming, validating, and generating reports from complex datasets,
            integrating seamlessly with SQL databases and Excel files,
            while providing interactive UI and CLI workflows for efficiency and accuracy."""
__version__ = '0.0.1' # type: ignore
with open(Path(__file__).parent / "requirements.txt") as f:
    requirements = f.read().splitlines()

readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name=__name__,
    version=__version__,
    author="surapatsue",
    author_email="nakarinsue@outlook.com",
    maintainer="nakarinsue",
    maintainer_email="nakarinsue@gosoft.co.th",
    description=__doc__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "Pro=Promotion_Counter.__main__:main",
            "RunPro=Promotion.__main__:main_app",
            "UIPro=Promotion.__main__:UI_app"
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
    ],
)
