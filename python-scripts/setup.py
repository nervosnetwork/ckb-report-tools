from setuptools import setup

setup(
    name="ckb-report-tools",
    version="0.0.1",
    author="Liya",
    description="Utils library for ckb data analyze",
    license="Apache 2.0",
    install_requires=[
        'configparser',
        'requests',
        'matplotlib',
        'seaborn',
        'opencv-python',
        'tabloo',   
        'openpyxl',
        'pillow',
        'python-dotenv',
    ],
)
