from setuptools import setup, find_packages

setup(
    name="systemloader",
    version="0.1.4",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click>=8.0.0",  # для CLI
    ],
    entry_points={
        "console_scripts": [
            "systemloader=systemloader.cli:main",  # точка входа для команды
        ],
    },
    project_urls={
        'GitFlic': 'https://gitflic.ru/project/alexyan/systemloader.git'
    },
    author="Alex Yanchenko",
    author_email="videoproc@yandex.ru",
    description="Загрузка движка",
    keywords="cli, systemloader",
    python_requires=">=3.12",
)
