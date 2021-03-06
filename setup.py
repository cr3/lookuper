from setuptools import (
    setup,
    find_packages,
)


setup(
    name='lookuper',
    use_scm_version=True,
    description='Lookup nested data structures',
    long_description=open('README.rst').read(),
    url='https://github.com/cr3/lookuper',
    author='Marc Tardif',
    author_email='marc@interunion.ca',
    setup_requires=['setuptools_scm'],
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    license='MIT',
    keywords='lookup nested',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
