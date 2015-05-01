from setuptools import setup

setup(
    name='docker-parse',
    version='0.1.8',
    description='Parse docker-run options from a running Docker container',
    url='https://github.com/iamfat/docker-parse',
    author="Jia Huang",
    author_email="iamfat@gmail.com",
    license='MIT',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Utilities',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',
    ],
    keywords='docker parse run options',
    packages=['docker_parse'],
    entry_points={
        'console_scripts': [
            'docker-parse=docker_parse:main',
        ],
    },
)
