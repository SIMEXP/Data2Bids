from setuptools import setup

setup(name='data2bids',
      version='1.0',
      description='Reorganize fmri files to make them BIDS compliant.',
      url='https://github.com/SIMEXP/Data2Bids',
      author='Loic TETREL',
      author_email='loic.tetrel.pro@gmail.com',
      license='MIT',
      packages=['data2bids'],
      scripts=['bin/data2bids'],
      install_requires=[
          'nibabel',
          'numpy',
      ],
      include_package_data = True,
      zip_safe=False)
