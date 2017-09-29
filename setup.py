from setuptools import setup, find_packages

if __name__ == "__main__":

    setup(
        name="mqtt",
        version="0.0.1a1",
        author="Amber Brown",
        author_email="the@cuteowl.online",
        url="https://github.com/hawkowl/mqtt",
        license="MIT",
        description="Pure Python sans-I/O MQTT protocol implementation.",
        classifiers=[
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python :: Implementation :: PyPy',
            'Topic :: Software Development :: Libraries :: Python Modules'
        ],
        package_dir={"": "src"},
        packages=find_packages('src'),
        install_requires=[
            "attrs",
            "bitstruct"
        ],
    )
