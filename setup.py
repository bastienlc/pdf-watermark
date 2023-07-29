from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()
setup(
    name="pdf-watermark",
    version="2.0.0",
    author="Bastien Le Chenadec",
    author_email="bastien.lechenadec@gmail.com",
    license="MIT License",
    description="A python CLI tool to add watermarks to a PDF",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bastienlc/pdf-watermark",
    py_modules=["watermark"],
    packages=find_packages(),
    install_requires=[requirements],
    python_requires=">=3.11",
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    entry_points="""
        [console_scripts]
        watermark=watermark:cli
    """,
)
