#!/usr/bin/python
#encoding: utf-8

from distutils.core import setup

setup(
	name='ConfigTreeView',
	version='0.1.0',
	author='Wesley Hansen',
	author_email='wes@ridersdiscount.com',
	packages=['configtreeview', 'configtreeview.tools'],
	scripts=['bin/config_example.py', 'bin/custom_treeview.py'],
	url='http://github.com/wrhansen/ConfigTreeView',
	license='LICENSE.txt',
	description='An easily configurable GtkTreeView implementation for pygtk.',
	long_description = open('README.txt').read(),
	install_requires = ["PyGTK >= 2.0.0", "simplejson"],
)
