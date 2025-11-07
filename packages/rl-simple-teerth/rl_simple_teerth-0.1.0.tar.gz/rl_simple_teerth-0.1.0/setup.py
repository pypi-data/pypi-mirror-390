from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='rl_simple_teerth',  # ⚠️ CHANGE THIS
    version='0.1.0',
    author='Teerth',  # ⚠️ CHANGE THIS
    author_email='teerth.chauhan75@nmims.in',  # ⚠️ CHANGE THIS
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
