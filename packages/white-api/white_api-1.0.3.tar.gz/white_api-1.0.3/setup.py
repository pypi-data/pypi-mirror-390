from setuptools import setup, find_packages

setup(
    name="white_api",
    version="1.0.3",
    author="devinpython",
    author_email="krostv321@gmail.com",
    description="Python client for White API (api.wscode.ru)",
    long_description="Python client library for interacting with White API",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=["requests>=2.25.0"],
    python_requires=">=3.7",
    keywords="api, white, gifts, stickers, nft, marketplace"
)