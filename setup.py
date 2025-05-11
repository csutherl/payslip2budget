from setuptools import setup, find_packages

setup(
    name="payslip2budget",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["PyPDF2","pdfplumber","datetime","requests"],
    extras_require-{
        'test': ['pytest'],
    },
    entry_points={{
        "console_scripts": [
            "payslip2budget=cli:main",
        ],
    }},
    author="Coty Sutherland",
    author_email="sutherland.coty@gmail.com",
    description="Convert payslip PDF to budget transactions (YNAB, Mint, EveryDollar, Monarch)",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires=">=3.7",
)