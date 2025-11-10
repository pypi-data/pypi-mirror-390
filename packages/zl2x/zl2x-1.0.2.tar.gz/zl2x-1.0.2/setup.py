from setuptools import setup, find_packages

setup(
    name="zl2x",
    version="1.0.2",
    description="Zalo API for Python",
    packages=find_packages(),
    install_requires=[
        'requests',
        'aiohttp',
        'aenum',
        'attr',
        'pycryptodome',
        'datetime',
        'munch',
        'websockets'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ]
)