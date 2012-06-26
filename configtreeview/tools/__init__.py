'''
The tools package contains modules that work alongside the ConfigTreeView implementation.
The tools package contains:

	*dataformatter* module
		A tool to convert a row of data that follows the structure defined by
		the ConfigTreeView implementation into the format that a GtkListStore
		expects( python list [] format) by mapping the index_map of the ConfigTreeView
		to the types list defined at ConfigTreeView runtime. 

	
'''
from dataformatter import DataFormatter
