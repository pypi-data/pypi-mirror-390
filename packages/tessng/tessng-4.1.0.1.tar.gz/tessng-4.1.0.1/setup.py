import sys
import setuptools
from wheel.bdist_wheel import bdist_wheel


# 获取当前Python版本
current_python_version: str = ".".join(map(str, [sys.version_info.major, sys.version_info.minor]))
print(f"当前Python版本为：{current_python_version}\n")

# 读取README.md文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 重写bdist_wheel
class CustomBdistWheel(bdist_wheel):
    def get_tag(self):
        # 如果Python版本是3.6
        if current_python_version == "3.6":
            python_tag = "cp36"
            abi_tag = "cp36m"
        # 如果Python版本是3.8
        elif current_python_version == "3.8":
            python_tag = "cp38"
            abi_tag = "cp38"
        # 如果Python版本是其他
        else:
            raise RuntimeError("Unsupported Python version")
        return python_tag, abi_tag, "win_amd64"

# 设置包信息
setuptools.setup(
    name="tessng",
    version="4.1.0.1",  # TODO (1)
    author="Jida Transportation",
    author_email="948117072@qq.com",
    description="TESS NG 4.1 Secondary Development (Python Version)",  # TODO (2)
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://jidatraffic.com:82/",
    python_requires="==3.6.*",  # TODO (3) ">=3.6, !=3.7.*, <3.9" or "==3.6.*"
    packages=setuptools.find_packages(),
    package_data={
        "tessng": ["*.dll", "*.pyd", "*.pyi", "*.exe", "TESS_PythonAPI_EXAMPLE"]
    },
    install_requires=[
        "shiboken2",
        "PySide2",
    ],
    license='MIT',
    license_files=['LICENSE'],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Education :: Computer Aided Instruction (CAI)",
        "Topic :: Games/Entertainment :: Simulation",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],  # TODO (4)
    cmdclass={
        "bdist_wheel": CustomBdistWheel
    },
    zip_safe=False,
    include_package_data=True,
)
