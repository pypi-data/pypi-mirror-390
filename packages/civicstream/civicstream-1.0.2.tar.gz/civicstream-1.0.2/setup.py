import setuptools

with open('README.rst', 'r') as fh:
   long_description = fh.read()

setuptools.setup(
   name='civicstream',
   version='1.0.2',
   author='Will Hedgecock',
   author_email='ronald.w.hedgecock@vanderbilt.edu',
   description='CivicAlert Streaming Data Capture and Visualization Tool',
   long_description=long_description,
   long_description_content_type='text/x-rst',
   url='https://github.com/vu-civic/tools',
   package_dir={'civicstream': 'app'},
   packages=['civicstream'],
   include_package_data=True,
   install_requires=[
      'numpy',
      'pyserial',
      'pygame',
      'PyOpenGL'
   ],
   classifiers=[
      'Programming Language :: Python :: 3',
      'Operating System :: OS Independent',
   ],
   python_requires='>=3.8',
   entry_points={
      'console_scripts': ['civicstream = civicstream.civicstream:main'],
   }
)
