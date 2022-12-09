from setuptools import setup, find_packages

setup(
    name="todo",
    version="0.0.1",
    packages=find_packages(include=["src"]),
    package_dir={"": "src"},
    install_requires=["click", "requests", "fastapi", "gunicorn"],
    entry_points={"console_scripts": ["todo-cli=todo.__main__:todo_cli"]},
)
