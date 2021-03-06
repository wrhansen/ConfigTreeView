========
Examples
========

This section details everything you need to get started using ``ConfigTreeView`` s.
This includes an example of how to use the ``ConfigTreeView``, how to create the
`config` structure and also how to create a custom wrapper to extend its uses
to fit your needs and finally how to use the `DataFormatter` to get your data
displayed correctly in the ``ConfigTreeView``.


How To Use a `ConfigTreeView`
-----------------------------

To use a `ConfigTreeView` is simple. In your python script there are only a couple
steps you need to follow:
	
	1. Initialize the `ConfigTreeView` with a config structure
	2. Apply the configuration to finish initializing the `ConfigTreeView`
	   components

Example:

	.. code:: python
	
		#Import the package
		from configtreeview import ConfigTreeView
		#Create the ConfigTreeView
		my_treeview = ConfigTreeView(config) #where `config` is a python dict config structure you already defined
		#Apply the configuration to the TreeView to finish initialization
		my_treeview._apply_config()


As you can see from the example, the API to use a ConfigTreeView is incredibly
simple. This is possible because the bulk of the work is done in how you define
and build the `config` structure.

How To Create/Build a `config` Structure
----------------------------------------

The config structure itself is just a python `dict` instance that contains the
information necessary to build all of the interface components for the `ConfigTreeView`.
For more information on what a `config` structure should look like, refer to
:doc:`HOW TO: Config File <how_to_config_file>`

As an example let's say we want a very simple treeview that contains two columns
that each have a title in their header, and contain a single string as the data
source for their respective `GtkCellRenderers`. The config structure for such a
case could look like this:

	.. code:: python
	
		{
			"index_names": {
				'column_1': {'markup': str},
				'column_2': {'markup': str}
			},
			"column_order": ["column_1", "column_2"],
			"columns":{
				"column_1":{
					"header":{
						"title": "Column1"
					},
					"renderers": {
							"indices":{"markup": True}
					}
				},
				"column_2":{
					"header":{
						"title": "Column2"
					},
					"renderers": {
							"indices":{"markup": True}
					}
				}
			}
		}


A Custom `ConfigTreeView` implmentation
---------------------------------------

Sometimes it is necessary to create your own implementation of a ``ConfigTreeView``.
This section describes the how? and the why?

Why?
====
There are many situations in your interface where you may need to subclass the
``ConfigTreeView`` so as to handle something extra that it doesn't cover. One
common situation that has come up in my own experiences has been with needing
to know one of the indexes represented in the data model for some dynamic use
throughout your application. For example: you would like to change the background
color of a cell in the treeview based on a user clicking on it and to do this
you need to know which index in a TreeModel row you're keeping that property.
Because of the way the data model is built for use in the ``ConfigTreeView``
with the actual indices hidden from the developer, this is not immediately an
easy task.

How?
====
But, fear not, the ``ConfigTreeView`` supplies an easy way to get around this.
To achieve this, you need to do a few things:

	1. Pass the index that you want(in dotted-key notation) to the `args`(or `kwargs`)
	   of the `treeview` dict within your config structure.
	2. Create a custom wrapper class that subclasses `ConfigTreeView`
	3. Make sure you override the `_handle_args` function of `ConfigTreeView`
	   that will be used to assign the args you specified in the config structure
	   to an attribute of your custom `ConfigTreeView` that you can use.

Example: building on from the above sample of a config structure...let's add a 
variable to our config that will be used to change the background of a cellrenderer:

	.. code:: python
	
		{
			"treeview": { #Added a 'treeview' key to supply custom args to our treeview
				"args": ['$index.bg_color'],#Pass the 'bg_color' index to our custom treeview
			},
			"index_names": {
				'bg_color': str,#Define the 'bg_color' variable--we'll make it a variable if we plan on using the same index for multiple renderers
				'column_1': {'markup': str},
				'column_2': {'markup': str}
			},
			"column_order": ["column_1", "column_2"],
			"columns":{
				"column_1":{
					"header":{
						"title": "Column1"
					},
					"renderers": {
							"indices":{"markup": True}
					}
				},
				"column_2":{
					"header":{
						"title": "Column2"
					},
					"renderers": {
							"indices":{"markup": True}
					}
				}
			}
		}

And then a corresponding custom treeview implementation would look something like
this:

	.. code:: python
	
		class CustomConfigTV(ConfigTreeView):
			'''
			An example of a custom ConfigTreeView wrapper
			used to get indices that were defined in
			the config structure
			'''
			
			def __init__(self, *args):
				ConfigTreeView.__init__(self, *args)
				#Any post-initializing stuff here
				#This is the place to do stuff *BEFORE* the
				#columns, renderers, and properties are set
				self.background_idx = None
			
			def _handle_args(self, background_idx):
				'''
				Override this function and set your custom args
				'''
				self.background_idx = background_idx

And now your treeview has an attribute `background_idx` that will contain the index
at which the 'bg_color' property you defined in the config will be formatted to.

Using DataFormatter to create rows
----------------------------------

Now that you've created a ``ConfigTreeView`` and initialized it with a config structure,
you're ready to start giving it data and using it!
In order to get the data properly displayed you need to do a few things:

	1. Make sure you understand the :doc:`ConfigTreeView data model <data_model>`
	   and use it to give properly constructed data sets
	2. Create a `DataFormatter` object, initializing it with your ``ConfigTreeView`` 's
	   `index_map`, and `types` structures.
	3. Create a `GtkTreeModel` to supply your TreeView with data
	4. Using the `DataFormatter` to yield formatted rows that can then be
	   appended to your `GtkTreeModel`

Example(using the config that was defined above):

	.. code:: python
	
		from configtreeview.tools import DataFormatter
		
		data = [ #The DataFormatter is expecting a list of dicts...each dict is a row following the ConfigTreeView Data Model
			{'column_1': {'markup': 'Some data here'}, 'column_2': {'markup': 'Column 2 data here'}},
			{'column_1': {'markup': 'More data col1'}, 'column_2': {'markup': 'Column 2 data here'}},
			{'column_1': {'markup': 'Even more data here'}, 'column_2': {'markup': 'Column 2 data here'}},
		]
		
		#Create the DataFormatter
		data_formatter = DataFormatter(my_treeview.index_map, mytreeview.types)
		
		#Get a treemodel
		liststore = my_treeview.get_treemodel() #Use this function to have your treeview build you a proper GtkTreeModel instance
		my_treeview.set_model(liststore)
		
		#Format the data rows for liststore and append them to it
		for row in data_formatter.get_rows(data):
			liststore.append(row)

And now the data should be displayed by your treeview!
		
		
		
		
		
		



		

