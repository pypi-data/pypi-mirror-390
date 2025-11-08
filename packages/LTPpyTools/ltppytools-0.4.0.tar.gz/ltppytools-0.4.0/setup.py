from setuptools import setup, find_packages

setup(
    name="LTPpyTools",  # 包名稱
    version="0.4.0",     # 版本號
    author="LTPLAX",
    author_email="no@no.com",
    description="A python package for any python program develop.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/LightingXT/Tools?tab=MIT-1-ov-file",  
    packages=find_packages(),  # 自動尋找子模組
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
