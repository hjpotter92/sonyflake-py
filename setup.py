from pathlib import Path

from setuptools import find_packages, setup

import sonyflake.about as about

if __name__ == "__main__":
    setup(
        name=about.NAME,
        version=about.VERSION,
        author=about.AUTHOR.get("name"),
        author_email=about.AUTHOR.get("email"),
        description="A distributed unique ID generator inspired by Twitter's Snowflake.",
        long_description=Path("README.md").read_text(),
        long_description_content_type="text/markdown",
        url="https://github.com/hjpotter92/sonyflake-py",
        packages=find_packages(),
        include_package_data=True,
        classifiers=[
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3 :: Only",
            "Programming Language :: Python :: Implementation",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Intended Audience :: Developers",
            "Topic :: Software Development :: Libraries :: Python Modules",
        ],
        python_requires=">=3.6",
    )
