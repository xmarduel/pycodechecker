#!/usr/bin/python

from distutils.core import setup

setup(
    name="pyanalysers",
    version="1.9.9_RC_1",
    description="GUI for PyLint, PyFlakes and PyMetrics",
    author="Xavier Marduel",
    maintainer_email="pyanalysers@web.de",
    url="",
    data_files=[('lib/site-packages/pyanalysers', ['RELEASE', 'RELNOTES'])],
    packages=["srcs"],
    package_data={'srcs': ['*.xrc', 'images/*.png', 'images/*.gif', 'images/*.ico', 'html/*.html', 'html/*.css', 'html/*.jpg']},
    scripts=["bin/pyanalysers", "bin/pyanalysers.bat"],
    long_description="""PythonCodeAnalysersApp is a GUI front end for PyLint, PyFlakes and PyMetrics"""
)


