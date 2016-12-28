from setuptools import setup

from goldschmidt import __version__

setup(name='goldschmidt',
      version=__version__,
      description='Readout a GU-3001D Milli-Gauss meter via USB/serial oport',
      long_description='Provides commandline readout and gui for the named instrument. For the name see https://en.wikipedia.org/wiki/Carl_Wolfgang_Benjamin_Goldschmidt who was an astronomer, mathematician and physicist and assistant to Gauss',
      author='Achim Stoessl',
      author_email="achim.stoessl@gmail.com",
      url='https://github.com/achim1/goldschmidt',
      #download_url="pip install pyosci",
      install_requires=['numpy>=1.11.0',
                        'matplotlib>=1.5.0'],
      license="GPL",
      platforms=["Ubuntu 14.04","Ubuntu 16.04"],
      classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.5",
        "Topic :: Scientific/Engineering :: Physics"
              ],
      keywords=["magnetometer", "gauss",\
                "GU-3001D", "gaussmeter", "Milli-Gauss Meter",\
                "readout", "physics", "engineering", "serial", "RS-232", "USB"],
      packages=['goldschmidt'],
      scripts=["bin/goldschmidt"],
      package_data={'goldschmidt': ['goldschmidt.mplstyle']}
      )
