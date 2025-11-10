"""
Author: DiChen
Date: 2025-08-07 17:57:01
LastEditors: DiChen
LastEditTime: 2025-08-09 15:02:34
"""

"""
Author: DiChen
Date: 2025-08-07 17:57:01
LastEditors: DiChen
LastEditTime: 2025-08-09 14:46:17
"""

"""
Author: DiChen
Date: 2025-08-01 10:51:13
LastEditors: DiChen
LastEditTime: 2025-08-07 16:50:16
"""

"""
inoyb - 基于mc.json配置的Gradio模型服务框架
Author: DiChen
Date: 2025-08-01
"""

from setuptools import setup, find_packages
import os


# 读取README文件作为长描述
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "inoyb - 基于mc.json配置的Gradio模型服务框架"


# 读取requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(req_path):
        with open(req_path, "r", encoding="utf-8") as f:
            return [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]
    return [
        "gradio>=4.0.0",
        "rasterio>=1.3.0",
        "matplotlib>=3.5.0",
        "Pillow>=8.0.0",
        "docker>=7.0.0",
    ]


setup(
    name="inoyb",
    version="1.1.9",
    author="DiChen",
    author_email="ldicccccc@gmail.com",
    description="极其友好的地理空间AI模型服务框架 - Docker化部署，支持Gradio界面",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/ldichen/It-is-none-of-your-business",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "inoyb=inoyb.cli:main",
        ],
    },
    keywords="gradio, model, service, framework, ml, ai, docker, geospatial, rasterio, gdal",
    project_urls={
        "Homepage": "https://github.com/ldichen/It-is-none-of-your-business",
        "Repository": "https://github.com/ldichen/It-is-none-of-your-business",
        "Documentation": "https://github.com/ldichen/It-is-none-of-your-business#readme",
        "Bug Reports": "https://github.com/ldichen/It-is-none-of-your-business/issues",
        "Changelog": "https://github.com/ldichen/It-is-none-of-your-business/releases",
    },
    package_data={
        "inoyb": ["static/*", "templates/*", "docker/templates/*"],
    },
)
