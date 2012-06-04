#!/usr/bin/python

from distutils.core import setup

setup(
	name='configtreeview',
	version='0.1.2',
	author='Wesley Hansen',
	author_email='wes@ridersdiscount.com',
	packages=['configtreeview', 'configtreeview.tools'],
	url='http://github.com/wrhansen/ConfigTreeView',
	license='GPLv3',
	description='An easily configurable GtkTreeView implementation for pygtk.',
	long_description = open('README.txt').read(),
	platforms=["POSIX", "Windows"],
	requires=["pygtk (>=2.0.0)", "simplejson"],
)
