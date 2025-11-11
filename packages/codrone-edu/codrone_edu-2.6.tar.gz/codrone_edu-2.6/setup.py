from setuptools import setup, find_packages
import sys

setup_requires = [
    ]

if sys.platform != 'emscripten':
    install_requires = [
        'pyserial>=3.5',
        'numpy',
        'colorama',
        'Pillow',
    ]
else:
    install_requires = []

dependency_links = [
    ]
desc = """\
Python package for controlling CoDrone EDU. 
"""

setup(
    name='codrone_edu',
    version='2.6',
    description='Python CoDrone EDU library',
    url='',
    author='',
    author_email='',
    keywords=[],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    setup_requires=setup_requires,
    dependency_links=dependency_links,
    python_requires='>=3.5',
    )
