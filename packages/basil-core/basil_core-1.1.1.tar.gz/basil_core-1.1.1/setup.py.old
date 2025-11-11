"""\
basil_core for postprocessing and inference with core simulations

Long description goes here...
"""

from datetime import date
from setuptools import find_packages, setup, Extension
import numpy
import os

#-------------------------------------------------------------------------------
#   Version
#-------------------------------------------------------------------------------
VERSIONFILE="__version__.py"
with open(VERSIONFILE, 'r') as F:
    _line = F.read()
__version__  = _line.split("=")[-1].lstrip(" '").rstrip(" '\n")

#-------------------------------------------------------------------------------
#   GENERAL
#-------------------------------------------------------------------------------
__name__        = "basil_core"
__date__        = date(2024, 5, 15)
__keywords__    = [
    "astronomy",
    "information analysis",
    "machine learning",
    "physics",
]
__status__      = "Alpha"


#-------------------------------------------------------------------------------
#   URLS
#-------------------------------------------------------------------------------
__url__         = "https://gitlab.com/xevra/basil-core"
__bugtrack_url__= "https://gitlab.com/xevra/basil-core/issues"


#-------------------------------------------------------------------------------
#   PEOPLE
#-------------------------------------------------------------------------------
__author__      = "Vera Delfavero"
__author_email__= "xevra86@gmail.com"

__maintainer__      = "Vera Delfavero"
__maintainer_email__= "xevra86@gmail.com"

__credits__     = ("Vera Delfavero",)


#-------------------------------------------------------------------------------
#   LEGAL
#-------------------------------------------------------------------------------
__copyright__   = 'Copyright (c) 2023 {author} <{email}>'.format(
    author=__author__,
    email=__author_email__
)

__license__     = 'MIT License'
__license_full__= '''
MIT License

{copyright}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''.format(copyright=__copyright__).strip()


#-------------------------------------------------------------------------------
#   PACKAGE
#-------------------------------------------------------------------------------

INCLUDE = [
           numpy.get_include(),
           os.path.join("src","basil_core","astro","coordinates"),
           os.path.join("src","basil_core","stats"),
           os.path.join("src","basil_core","array_tools"),
           os.path.join("src","basil_core","c_utils"),
           os.path.join("src","basil_core","astro"),
           os.path.join("src","basil_core","astro","orbit"),
          ]

ext_modules = [
               Extension("basil_core.astro.coordinates._coordinates",
                         sources = [os.path.join("src","basil_core","astro", "coordinates", "_coordinates.c")],
                         py_limited_api=True,
                         include_dirs = INCLUDE,
                        ),
               Extension("basil_core.astro.coordinates._tides",
                         sources = [os.path.join("src","basil_core","astro", "coordinates", "_tides.c")],
                         py_limited_api=True,
                         include_dirs = INCLUDE,
                        ),
               Extension("basil_core.astro.coordinates._spin",
                         sources = [os.path.join("src","basil_core","astro", "coordinates", "_spin.c")],
                         py_limited_api=True,
                         include_dirs = INCLUDE,
                        ),
               Extension("basil_core.stats._distance",
                         sources = [os.path.join("src","basil_core","stats", "_distance.c")],
                         py_limited_api=True,
                         include_dirs = INCLUDE,
                        ),
               Extension("basil_core.stats._relative_entropy",
                         sources = [os.path.join("src","basil_core","stats", "_relative_entropy.c")],
                         py_limited_api=True,
                         include_dirs = INCLUDE,
                        ),
               Extension("basil_core.astro.orbit._GW",
                         sources = [os.path.join("src","basil_core","astro", "orbit", "_GW.c")],
                         py_limited_api=True,
                         include_dirs = INCLUDE,
                        ),
               Extension("basil_core.astro.orbit._kepler",
                         sources = [os.path.join("src","basil_core","astro", "orbit", "_kepler.c")],
                         py_limited_api=True,
                         include_dirs = INCLUDE,
                        ),
               Extension("basil_core.astro.orbit._DWD_RLOF",
                         sources = [os.path.join("src","basil_core","astro", "orbit", "_DWD_RLOF.c")],
                         py_limited_api=True,
                         include_dirs = INCLUDE,
                        ),
               Extension("basil_core.array_tools._indexer",
                         sources = [os.path.join("src","basil_core","array_tools", "_indexer.c")],
                         py_limited_api=True,
                         include_dirs = INCLUDE,
                        ),
               Extension("basil_core.stats._schechter",
                         sources = [os.path.join("src","basil_core","stats", "_schechter.c")],
                         py_limited_api=True,
                         include_dirs = INCLUDE,
                        ),
              ]
PACKAGE_DATA = {
    "basil_core": [
        "astro/relations/early_frac_of_GSM_metallicity/Peng2015/stellarMZR-SF.TXT",
        "astro/relations/early_frac_of_GSM_metallicity/Peng2015/stellarMZR-passive.txt",
        "astro/relations/AGND/Lyon2024/Lyon2024AGNPhi.dat",
        "astro/relations/AGND/Lyon2024/LICENSE.txt",
    ],
}
# Thank you:
# https://stackoverflow.com/questions/6028000/how-to-read-a-static-file-from-inside-a-python-package

DOCLINES = __doc__.split("\n")

CLASSIFIERS = [
"Development Status :: 3 - Alpha",
"Programming Language :: Python :: 3",
"Operating System :: OS Independent",
"Intended Audience :: Science/Research",
"Topic :: Scientific/Engineering :: Astronomy",
"Topic :: Scientific/Engineering :: Physics",
"Topic :: Scientific/Engineering :: Information Analysis",
]

# Matching the numpy version of the installation is a hacky fix for this bug:
# https://numpy.org/devdocs/user/troubleshooting-importerror.html#c-api-incompatibility
# If you have a beter solution please open an issue or pull request
REQUIREMENTS = {
    "install" : [
        "h5py>=2.7.0",
        "numpy>=1.21.6",
        "matplotlib>=2.0.0",
        "scipy>=1.2.0",
        "six>=1.10.0",
        "fast_histogram>=0.10",
        "xev-data>=0.0.7",
        "astropy",
        "pathlib",
    ],
    "setup" : [
        "pytest-runner",
    ],
    "tests" : [
        "pytest",
    ]
}

ENTRYPOINTS = {
    "console_scripts" : [
        # Example:
        # script_name = module.2.import:function_to_call
    ]
}


metadata = dict(
    name        =__name__,
    version     =__version__,
    description =DOCLINES[0],
    long_description='\n'.join(DOCLINES[2:]),
    keywords    =__keywords__,

    author      =__author__,
    author_email=__author_email__,

    maintainer  =__maintainer__,
    maintainer_email=__maintainer_email__,

    url         =__url__,
#    download_url=__download_url__,

    license     =__license__,

    classifiers=CLASSIFIERS,

    package_dir ={"": "src"},
    package_data=PACKAGE_DATA,
    packages=find_packages("src"),

    install_requires=REQUIREMENTS["install"],
    setup_requires=REQUIREMENTS["setup"],
    tests_require=REQUIREMENTS["tests"],

    entry_points=ENTRYPOINTS,
    ext_modules=ext_modules,
    python_requires=">=3.9",
)

setup(**metadata)
