import pathlib
import setuptools
from torch.utils.cpp_extension import BuildExtension, CUDAExtension

include_dirs = ["torchopticsy/CUDA"]  # 指定包含目录

ext_modules = [
    CUDAExtension(
        name="opticsyCUDA.Utils",  # 命名第一个扩展模块
        sources=["torchopticsy/CUDA/Utils.cu"],  # 指定第一个CUDA源文件
        include_dirs=include_dirs,
        extra_compile_args={"cxx": ["-O2"], "nvcc": ["-O2"]},
    ),
]

setuptools.setup(
    name="torchopticsy",
    version="0.10.2",
    description="PyTorch-based optics caculation",
    long_description="",  # pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    author="YuningYe",
    author_email="1956860113@qq.com",
    license="MIT",
    packages=setuptools.find_packages(),
    install_requires=["torch", "opencv-python", "matplotlib"],
    include_package_data=True,
    ext_modules=ext_modules,  # 包含 CUDA 扩展
    cmdclass={"build_ext": BuildExtension},  # 使用 BuildExtension 编译 CUDA 扩展
)
