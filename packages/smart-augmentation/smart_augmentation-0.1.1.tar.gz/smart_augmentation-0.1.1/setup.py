from setuptools import setup, find_packages

setup(
    name="smart_augmentation",
    version="0.1.1",
    author="Divine Gupta",
    author_email="guptadivine0611@gmail.com",
    description="An easy-to-use image data augmentation library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=["opencv-python", "numpy"],
    python_requires=">=3.7",
)
