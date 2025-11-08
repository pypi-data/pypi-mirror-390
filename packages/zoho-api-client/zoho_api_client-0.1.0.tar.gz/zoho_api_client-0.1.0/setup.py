from setuptools import setup, find_packages
import os


# Leer README
def read_file(filename):
    here = os.path.abspath(os.path.dirname(__file__))
    try:
        with open(os.path.join(here, filename), encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""


# Leer requirements con filtrado mejorado
def read_requirements(filename):
    here = os.path.abspath(os.path.dirname(__file__))
    requirements = []

    try:
        with open(os.path.join(here, filename), encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Ignorar líneas vacías, comentarios y referencias a otros archivos
                if line and not line.startswith('#') and not line.startswith('-r'):
                    requirements.append(line)
    except FileNotFoundError:
        pass

    return requirements


setup(
    name="zoho-api-client",
    version="0.1.0",
    author="Victor",
    author_email="tu@email.com",
    description="Cliente Python para las APIs de Zoho (CRM, Books, Inventory)",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/CodeDeveloperV/zoho-api-client",
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.31.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "black>=24.0.0",
            "ruff>=0.1.0",
            "mypy>=1.8.0",
            "types-requests>=2.31.0",
            "python-dotenv>=1.0.0",
            "ipython>=8.12.0",
        ],
    },
    keywords="zoho api crm books inventory client sdk",
    project_urls={
        "Bug Reports": "https://github.com/CodeDeveloperV/zoho-api-client/issues",
        "Source": "https://github.com/CodeDeveloperV/zoho-api-client",
        "Documentation": "https://github.com/CodeDeveloperV/zoho-api-client#readme",
    },
    include_package_data=True,
    zip_safe=False,
)