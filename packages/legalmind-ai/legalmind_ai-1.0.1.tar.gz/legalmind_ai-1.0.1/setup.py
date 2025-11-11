from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="legalmind-ai",
    version="1.0.1",
    author="LegalMind AI",
    author_email="contact@legalmind.ai",
    description="AI-Powered Legal Assistant for Indonesian Law",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/creatoross/legalmind-ai",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Legal Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9", 
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "python-dotenv>=0.19.0",
        "numpy>=1.21.0",
        "scikit-learn>=1.0.0",
    ],
    entry_points={
        'console_scripts': [
            'legalmind=legalmind.cli:main',
        ],
    },
    include_package_data=True,
)
