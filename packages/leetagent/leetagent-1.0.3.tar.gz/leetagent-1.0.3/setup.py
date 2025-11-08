"""
Setup configuration for LeetCode Agent Automation
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = []
with open('requirements.txt') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('-'):
            requirements.append(line)

setup(
    name="leetagent",
    version="1.0.3",
    author="Satyam Yadav",
    author_email="satyamyadavaiml@gmail.com",
    description="AI-powered LeetCode automation tool with Gemini AI and browser automation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/satyamyadav/leetagent",
    project_urls={
        "Documentation": "https://github.com/satyamyadav/leetagent#readme",
        "Source": "https://github.com/satyamyadav/leetagent",
        "Issues": "https://github.com/satyamyadav/leetagent/issues",
    },
    packages=find_packages(exclude=['tests', 'tests.*', 'venv', 'venv.*']),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "leetagent=leetagent.__main__:main",
            "leetagent-doctor=leetagent.post_install:print_instructions",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", ".env.example"],
    },
    keywords=[
        "leetcode",
        "automation",
        "ai",
        "gemini",
        "selenium",
        "coding",
        "interview-prep",
        "langchain",
    ],
)
