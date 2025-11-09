from setuptools import setup, find_packages  # <- dòng này rất quan trọng!

setup(
    name="text_python",
version="0.6",  # nhớ tăng version mới
    packages=find_packages(),
    install_requires=[
        "pygame>=2.6.1"
    ],
    python_requires=">=3.8",
)


