# To install local package for virtual environment
from setuptools import find_packages, setup

setup(
    name='mcqgenrator',
    version='0.0.1',
    author='NK Bangar',
    author_email='nand.bangar@gmail.com',
    install_requires=["openai","langchain","streamlit","python-dotenv","PyPDF2"],
    packages=find_packages()
)