#!/usr/bin/python

from setuptools import setup, find_packages

required = ['simplejson']
try:
	import pygtk
	pygtk.require('2.0')
except (ImportError,AssertionError) as e:
	print "ImportError!: %s" % e
	print "Adding 'pygtk >= 2.0.0' to install_requires list"
	required.append( 'pygtk >= 2.0.0' )

setup(
	name='configtreeview',
	version='0.1.3',
	author='Wesley Hansen',
	author_email='wes@ridersdiscount.com',
	packages=find_packages(),
	url='http://github.com/wrhansen/ConfigTreeView',
	license='GPLv3',
	description='An easily configurable GtkTreeView implementation for pygtk.',
	long_description = open('README.txt').read(),
	platforms=["POSIX", "Windows"],
	install_requires=required
)
