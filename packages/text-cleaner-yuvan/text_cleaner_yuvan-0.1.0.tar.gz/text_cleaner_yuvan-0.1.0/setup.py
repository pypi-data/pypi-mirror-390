from setuptools import setup, find_packages

setup(
    name="text_cleaner_yuvan",
    version="0.1.0",
    author="Yuvan Jain",
    author_email="jainyuvan769@example.com",
    description="A simple text cleaning tool for NLP.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/YuvanJain/text_cleaner",
    packages=find_packages(),
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Education",
        "Topic :: Text Processing :: Linguistic",
    ],
    include_package_data=True,
    install_requires=[],
)
