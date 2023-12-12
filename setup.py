from setuptools import find_packages, setup
from itertools import chain

setup(
    name="pokegym",
    description="Pokemon Red Gymnasium environment for reinforcement learning",
    long_description_content_type="text/markdown",
    version=open('pokegym/version.py').read().split()[-1].strip("'"),
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pyboy<2.0.0',
        'gymnasium>=0.29',
        'numpy',
    ],
    entry_points = {
        'console_scripts': [
            'pokegym.play = pokegym.environment:play'
        ]
    },
    python_requires=">=3.8",
    license="MIT",
    # @pdubs: Put your info here
    author="Joseph Suarez",
    author_email="jsuarez@mit.edu",
    url="https://github.com/PufferAI/pokegym",
    keywords=["Pokemon", "AI", "RL"],
    classifiers=[
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
