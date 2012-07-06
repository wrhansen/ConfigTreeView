
The Config Structure
============================
We needed something that could initialize the treeview's gui components and their
properties( TreeViewColumn, CellRenderer, and the TreeView itself ), but also
have an insight into what each renderer is expecting of the data( for setting up
cell-specific renderer properties, or which data it's going to display) without
having to specifically define the actual indices into the data that these
components are searching for( the treeview will be able to handle that internally
upon initialization using the config file)


Complete Structure, with every possible key:
---------------------------------------------

Note: This structure details every possible key or key arrangement for
the sake of it. It can appear to be complex and overwhelming at first glance,
but don't fret. If a key that isn't required isn't used at all for the 
ConfigTreeView you want to build, then don't have to include that key. This
applies to top-level keys as well. This functionality allows the user
to rapidly and easily build TreeViews.

.. code:: python

	{
		"treeview":{
			"properties":{ #This struct will contain all treeview properties---meaning things that can be set using `treeview.set_property( property, value)`
				"rules-hint": True,#<---A property of GtkTreeView
				"headers-clickable": True,
			},
			"args": [ #Positional arguments to send to a custom ConfigTreeView--can be indices, or custom values
				"$index.record_open_bool", #This is how you assign an index as an argument to the ConfigTreeView
				"$index.column_one.1.markup", #An example assigning an index from a column that has multiple renderers--a number in a 'dotted' string represents the index in the list of renderers
			],
			"kwargs": {}, #Keyword arguments to send to a custom ConfigTreeView--same rules as "args"
			'bg': None, #Set background color, bg-even and bg-odd override this option
			'bg-even': '#A2C879', #Set even-row background color...must be accompanied by bg-odd
			'bg-odd': '#6794AB', #Set odd-row background color...must be accompanied by bg-even
			'selection-mode': 'SELECTION_SINGLE', #The selection mode of the TreeView...must be one of SELECTION_NONE, SELECTION_SINGLE, SELECTION_BROWSE, SELECTION_MULTIPLE
			'selection-color': '#bfd3e7', #Change the color of the selection bar--value can be a valid color name or hex string
		},
		"treemodel": { #You can tell the TreeView to build you a custom TreeModel(via the get_treemodel() function)
			"module": "package.subpackage.module", #The package/module location of the class to import
			"class": "CustomTreeModelClass", #Your custom GtkTreeModel implementation
			"args": [], #The positional arguments to send to the TreeModel's _handle_args method
			"kwargs": {}, #The keyword arguments to send to the TreeModel's _handle_args method
		},
		"index_names":{ #Maps the given index into the type of data it will store
			"record_open_bool": bool, #This is how you define a type of 'bool' for an index that will be used by more than one column's renderer
			"order_status":{ #This is how you specifically define types for a certain column(that contains only a single CellRenderer)
				"markup": str, #The `markup` property of the cell renderer
			},
			"column_one":[ #This is how you define types for columns with multiple renderers
				{ "markup": str, "cell-background": str},
				{ "pixbuf": "gtk.gdk.Pixbuf"},
			],
		},
		"column_order": ['column_one', 'order_status'], #Define the order the columns are appended in the treeview. List the column names in the order you want them appended to the TreeView
		"macros": { #Define macros--a convenience for assiging the same properties to multiple columns or renderers
			"col-default": {
				"expand": True,
				"resizable": True,
				"clickable": True,
				"reorderable": True,
			}
		},
		"columns": {
			"column_one": { #A column named "column_one"--the name is used when determing: where columns go in the TreeView, which indices a column's renderers will use, and their types
				"macros": ["col-default"], #Assign a macro( by name )
				'header': { #This struct contains information to create the header for this column. A header can be a string or a custom widget. Defaults to do nothing
					'title': 'Column1', #A simple text label displaying the title(This is a fallback to the custom widget)
					'module': None, #The module that contains the header widget, None defaults to the gtk module
					'class': 'Button', #A string of the class( must inherit gtk.Widget), to set the header widget to. None defaults to gtk.Label(If 'title' key isn't present)
					'args': [], #Positional arguments to pass to 'class'
					'kwargs': {}, #Keyword arguments to pass to 'class'
				},
				"properties": { #This struct will contain all TreeViewColumn properties that can be set using treeviewcolumn.set_property(property, value)
					"resizable": True,
					"visible": True,
					"max-width": 100,
				},
				"renderers":[ #Create the Renderers( use a list if multiple renderers in one column)
					{
						'pack': 'pack_start', #Either 'pack_start' or 'pack_end', if this is None, defaults to pack_start
						'expand': True, #Sets the packing method 'expand' property, if this is None, defaults to True
						'module': None, #The module that contains the renderer, None if it's in the gtk module
						'class': 'CellRendererText', #A string name of the  CellRenderer class to use( must inherit gtk.CellRenderer )...if this is None, defaults to gtk.CellRendererText
						'args': [], #Positional arugments to pass to 'class', if None, don't pass args to 'class'
						'kwargs': {}, #Keyword arguments to pass to 'class', if None don't pass kwargs to 'class'
						'properties': { #This struct contains all properties that each row will have by using cellrenderer.set_property( property, value), if 'properties' doesn't exist(or None), then no props set.
							'height': 25,
							'xpad': 5,
							'font': 'Times New Roman 13',
						},
						'indices': { #This struct contains all properties that are set from the treemodel data...using column.add(attribute,property, index), None sets no attributes
							#These indices are determined at runtime when the ConfigTreeView is initialized.
							#You can either set them by assigning them a name( if one index will be shared by multiple renderers)
							#	NOTE: You must assign by a name that exists in the 'index_names' key of this configuration file
							#Or you can set them by setting a property value to True, telling the TreeView that this one is unique
							"markup": True,	#This CellRendererText needs its own 'markup' index in the data model
							"cell-background-set": "record_open_bool"	#All columns will share this index
						
						}
					},
					{ #The second renderer in the "column_one" column
						'class': 'CellRendererPixbuf',
						'indices': {
							'pixbuf': True, #This CellRendererPixbuf needs its own 'pixbuf' index in the data model
							'cell-background-set': 'record_open_bool', #All columns will share this index
						},
										
					},
				],
			},
			"order_status": { #Another column, this one named "order_status"
				'header': {
					'title': 'Order Status',
				},
				'properties': {
					'resizable': True,
				},
				'renderers': { #A single renderer can be defined as a single dict instead of as a list
					'markup': True, #This CellRendererText needs its own 'markup' index in the data model
					'cell-background-set': 'record_open_bool'#All columns will share this index
				},
			
			}
		}
	
	}
