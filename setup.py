from setuptools import setup, find_packages
from typing import List

def get_requirements() -> List[str]:
    """
    This function will return the list of requirements as list of strings.
    """
    try:
        with open("requirements.txt", "r") as f:
            lines = f.readlines()
            ## Process each line
            requirements_list = [line.strip() for line in lines if line and line != "-e ."]
            return requirements_list
    except FileNotFoundError:
        print("The requirements.txt file is not found")


setup(
    name= "NetworkSecurity",
    version= "0.0.1",
    author= "SaiVardhan4694",
    author_email= "makkapatimrk@gmail.com",
    packages= find_packages(),
    install_requires= get_requirements(),
)