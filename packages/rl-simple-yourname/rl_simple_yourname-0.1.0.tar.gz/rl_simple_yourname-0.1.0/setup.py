from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='rl_simple_yourname',  # ⚠️ CHANGE THIS
    version='0.1.0',
    author='Your Name',  # ⚠️ CHANGE THIS
    author_email='your.email@example.com',  # ⚠️ CHANGE THIS
    description='Simple RL utilities for epsilon-greedy and TD error',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
