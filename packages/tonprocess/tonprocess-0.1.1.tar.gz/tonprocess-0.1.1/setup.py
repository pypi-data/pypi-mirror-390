from setuptools import setup, find_packages
import os

# Read README.md safely
def read_long_description():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "A secure and easy-to-use Python wrapper for Trino with pandas-friendly output."

setup(
    name="tonprocess",
    version="0.1.1",
    author="Kamlesh Kumar",
    author_email="kammlesh4@gmail.com",
    description="Secure Trino connector for Python with pandas output",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/kamlesh1114/pwpy_db",

    project_urls={
        "Source": "https://github.com/kamlesh1114/pwpy_db",
        "Issues": "https://github.com/kamlesh1114/pwpy_db/issues",
    },

    packages=find_packages(),
    include_package_data=True,

    install_requires=[
        "trino>=0.319",
        "pandas>=1.0",
        "python-dotenv>=1.0",
        "psutil>=5.9",
        "requests>=2.20",
        "cryptography>=41.0",
    ],

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    keywords="trino presto sql database connector pandas secure encryption",

    python_requires=">=3.8",
)
