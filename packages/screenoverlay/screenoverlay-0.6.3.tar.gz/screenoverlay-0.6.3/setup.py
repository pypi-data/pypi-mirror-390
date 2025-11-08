from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="screenoverlay",
    version="0.6.3",
    author="ScreenStop",
    author_email="ppnicky@gmail.com",
    description="Cross-platform screen overlay with blur, black, white, and custom modes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pekay-ai/screenoverlay",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Graphics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.7",
    install_requires=[
        'pyobjc-framework-Cocoa; platform_system=="Darwin"',
        'screeninfo',
    ],
    extras_require={
        "dev": ["pytest", "twine", "wheel"],
    },
)

