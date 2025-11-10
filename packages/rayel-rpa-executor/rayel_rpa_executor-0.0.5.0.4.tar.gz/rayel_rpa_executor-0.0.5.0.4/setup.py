from setuptools import find_packages, setup  # pyright: ignore[reportMissingModuleSource]

setup(
    name="rayel-rpa-executor",  # 项目名称
    version="0.0.5.0.4",  # 项目版本 TODO：每次改这个版本
    packages=find_packages(),  # 自动发现项目中的包
    install_requires=[  # 项目依赖包
        "pydantic>=2.7.4",
        "python-dotenv>=1.0.1",
        "aiohttp>=3.10.9",
        "protobuf>=5.27.2",
        "grpcio>=1.66.2",
        "GitPython>=3.1.0",
        "playwright>=1.55.0"
    ],
    extras_require={
        "dev": [
            "ruff>=0.3.0",
            "grpcio-tools>=1.66.2",
        ],
    },
    python_requires=">=3.8",
    long_description=open("README.md").read(),  # 读取 README.md 文件作为长描述
    long_description_content_type="text/markdown",  # 长描述格式
    author="laizezhong",
    author_email="914660773@qq.com",
    description="a high performance distributed task scheduler and retry management center",
    # url="https://gitee.com/opensnail/snail-job-python",  # 项目主页
    classifiers=[  # 项目的分类信息
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="distributed, task-scheduler, job-scheduler, retry-management",
)
