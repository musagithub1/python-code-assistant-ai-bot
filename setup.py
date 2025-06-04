from setuptools import setup, find_packages

setup(
    name="python_bot_upgraded",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai",
        "flask",
        "rich"
    ],
    entry_points={
        'console_scripts': [
            'python_bot=python_bot_upgraded.main:main',
        ],
    },
)
