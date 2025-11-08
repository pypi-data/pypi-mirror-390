from setuptools import setup, find_packages

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='niceplotpy',
    version='0.10.2',
    description='A package collecting things to make nice plots from root files',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.cern.ch/jwuerzin/nice-plot',
    author='Jonas Wuerzinger',
    author_email='jonas.wuerzinger@tum.de',
    packages=find_packages(),
    package_data={'': ['data/*.csv']},
    install_requires=['numpy',
                      'Click',
                      'matplotlib>=3.7.2',
                      'pyyaml',
                      'uproot>=5.0',
                      'awkward>=2.6.3',
                      'pandas',
                      'atlasify',
                      'importlib-metadata',
                      'tqdm',
                      'structlog'
                      ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    entry_points={
        'console_scripts': [
            'niceplot = niceplot.__main__:niceplot',
        ],
    },
)    
